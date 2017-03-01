//
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <modbus.h>
#include <modbus-rtu.h>

#define NB_LOOP 250
#define SERVER_ID       0x02
#define ADDRESS_START   0x00

int main(int argc, char* argv[])
{
	modbus_t *ctx;
	int rc;
	int nb_read_fail;
	int nb_write_fail;
	int nb_loop = NB_LOOP;
	int addr;
	int nb;
	int i;
	int a;
	uint8_t *tab_rq_bits;
	uint8_t *tab_rp_bits;
	uint16_t *tab_rq_registers;
	uint16_t *tab_rw_rq_registers;
	uint16_t *tab_rp_registers;
	


	ctx = modbus_new_rtu("/dev/ttyUSB0", 19200, 'N', 8, 1);
	//modbus_set_error_recovery(ctx,MODBUS_ERROR_RECOVERY_LINK);	
	modbus_set_slave(ctx, SERVER_ID);
	modbus_set_debug(ctx, TRUE);
	
	if (modbus_connect(ctx) == -1) 
	{
		fprintf(stderr, "Connection failed: %s\n",
			modbus_strerror(errno));
		modbus_free(ctx);
		return -1;
	}
	// if (modbus_rtu_set_serial_mode(ctx, MODBUS_RTU_RS485) == -1) {
 //            printf("error!!!!! %s\n", modbus_strerror(errno));
 //    }
	
	
    printf("mode: %d\n", modbus_rtu_get_serial_mode(ctx));

	 /* Allocate and initialize the different memory spaces */
	addr = ADDRESS_START;
	nb = 0x08;
	
	tab_rq_bits = (uint8_t *) malloc(nb * sizeof(uint8_t));
	memset(tab_rq_bits, 0, nb * sizeof(uint8_t));

	tab_rp_bits = (uint8_t *) malloc(nb * sizeof(uint8_t));
	memset(tab_rp_bits, 0, nb * sizeof(uint8_t));

	tab_rq_registers = (uint16_t *) malloc(nb * sizeof(uint16_t));
	memset(tab_rq_registers, 0, nb * sizeof(uint16_t));

	tab_rp_registers = (uint16_t *) malloc(nb * sizeof(uint16_t));
	memset(tab_rp_registers, 0, nb * sizeof(uint16_t));

	tab_rw_rq_registers = (uint16_t *) malloc(nb * sizeof(uint16_t));
	memset(tab_rw_rq_registers, 0, nb * sizeof(uint16_t));

	nb_read_fail = 0;
	nb_write_fail = 0;
	
	for(a = 0; a< nb_loop;a++)
	{
		tab_rq_registers[0] = a;
		tab_rq_registers[1] = 250-a;

	/*MULTIPLE REGISTERS */
	rc = modbus_write_registers(ctx, addr, nb, tab_rq_registers);
	if (rc != nb) 
	{
		printf("ERROR modbus_write_registers (%d)\n", rc);
		printf("Address = %d, nb = %d\n", addr, nb);
		nb_write_fail++;
	} 
	//else 
	//{
		rc = modbus_read_registers(ctx, addr, nb, tab_rp_registers);
		if (rc != nb) 
		{
			printf("ERROR modbus_read_registers (%d)\n", rc);
			printf("Address = %d, nb = %d\n", addr, nb);
			nb_read_fail++;
		} 
		else 
		{
			
			for (i=0; i<nb; i++) 
			{
				
				printf("Address = %d, value set:%d (0x%X), value read:%d (0x%X)\n",
							addr, tab_rq_registers[i], tab_rq_registers[i],
							tab_rp_registers[i], tab_rp_registers[i]);
			}
		}
	//}
	printf("****************************\n");
	}
	modbus_close(ctx);
	modbus_free(ctx);

	printf("packets sent %d\n",nb_loop);
	printf("read errors: %d\n",nb_read_fail);
	printf("write errors: %d\n",nb_write_fail);
	return 0;
}

