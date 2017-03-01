/*
 * Copyright Â© 2008-2010 StÃ©phane Raimbault <stephane.raimbault@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>

#include <modbus.h>

enum {
    TCP,
    RTU
};

int main(int argc, char *argv[])
{
    int socket;
    modbus_t *ctx;
    modbus_mapping_t *mb_mapping;
    int rc;
    int use_backend;

     /* TCP */
    if (argc > 1) {
        if (strcmp(argv[1], "tcp") == 0) {
            use_backend = TCP;
        } else if (strcmp(argv[1], "rtu") == 0) {
            use_backend = RTU;
        } else {
            printf("Usage:\n  %s [tcp|rtu] - Modbus client to measure data bandwith\n\n", argv[0]);
            exit(1);
        }
    } else {
        /* By default */
        use_backend = RTU;
    printf("bandwidth-server-one:\n Running in RTU mode - Modbus client to measure data bandwith\n\n");
    }

    if (use_backend == TCP) {
        printf("Waiting for TCP connection\n");
        ctx = modbus_new_tcp("127.0.0.1", 1502);
        socket = modbus_tcp_listen(ctx, 1);
        modbus_tcp_accept(ctx, &socket);
        printf("TCP connection started!\n");
    } else {
        printf("Waiting for Serial connection\n");
        
        ctx = modbus_new_rtu("/dev/ttyUSB0", 19200, 'N', 8, 1);
        if (ctx == NULL) {
            fprintf(stderr, "unable to connect to device\n");
        }
        // modbus_connect(ctx);
        modbus_set_slave(ctx, 0x02);

        
        if (modbus_connect(ctx) == -1) {
            fprintf(stderr, "Connection failed: %s\n", modbus_strerror(errno));
            modbus_free(ctx);
            return -1;
        }
        //if (modbus_rtu_set_serial_mode(ctx, MODBUS_RTU_RS485) == -1) {
        //    printf("error!!!!!\n");
        //}

        // modbus_set_master(ctx, 1);
        printf("Serial connection started!\n");
    }

    uint16_t tab_reg[72];
    int i;
//    if (modbus_write_register(ctx, 69, 3) == -1) {
//	fprintf(stderr, "error writnig to reg 6");
//    }
    rc = modbus_read_registers(ctx, 0, 72, tab_reg);
    while (rc == -1) {
        fprintf(stderr, "%s\n", modbus_strerror(errno));
        modbus_read_registers(ctx, 0, 72, tab_reg);
    }
	printf("%d", rc);
    for (i=0; i < 72; i++) {
        printf("reg[%d]=%d (0x%X)\n", i, tab_reg[i], tab_reg[i]);
    }
	tab_reg[69] = 2;
       if (modbus_write_registers(ctx,69,1,tab_reg) == -1) {
        fprintf(stderr, "error writnig to reg 6");
    }

    // uint8_t raw_req[] = { 0xFF, 0x03, 0x00, 0x01, 0x0, 0x05 };
    // int req_length;
    // uint8_t rsp[MODBUS_TCP_MAX_ADU_LENGTH];



    // req_length = modbus_send_raw_request(ctx, raw_req, 6 * sizeof(uint8_t));
    // printf("1\n");
    // modbus_receive_confirmation(ctx, rsp);
    // printf("%d\n", rsp);
    // printf("%d\n", req_length);
    // mb_mapping = modbus_mapping_new(MODBUS_MAX_READ_BITS, 0,
    //                                 MODBUS_MAX_READ_REGISTERS, 0);
    // if (mb_mapping == NULL) {
    //     fprintf(stderr, "Failed to allocate the mapping: %s\n",
    //             modbus_strerror(errno));
    //     modbus_free(ctx);
    //     return -1;
    // }

    // for(;;) {
    //     uint8_t query[MODBUS_TCP_MAX_ADU_LENGTH];

    //     rc = modbus_receive(ctx, query);
    //     if (rc >= 0) {
    //     printf("Replying to request.\n");
    //         modbus_reply(ctx, query, rc, mb_mapping);
    //     } else {
    //         /* Connection closed by the client or server */
    //         break;
    //     }
    // }

    // printf("Quit the loop: %s\n", modbus_strerror(errno));

    // int reg4001 =  modbus_read_registers(ctx, int addr, int nb, uint16_t *dest);

    close(socket);
    modbus_free(ctx);

    return 0;
}
