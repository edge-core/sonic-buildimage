/* -------------------------------------------------------------------- 

	 * A hwmon driver for the CIG cs6436-56P
	 *
	 * Copyright (C) 2018 Cambridge, Inc.
	 *
	 * This program is free software; you can redistribute it and/or modify
	 * it under the terms of the GNU General Public License as published by
	 * the Free Software Foundation; either version 2 of the License, or
	 * (at your option) any later version.
	 *
	 * This program is distributed in the hope that it will be useful,
	 * but WITHOUT ANY WARRANTY; without even the implied warranty of
	 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	 * GNU General Public License for more details.
	 *
	 * You should have received a copy of the GNU General Public License
	 * along with this program; if not, write to the Free Software
	 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
	 */

/* --------------------------------------------------------------------	*/

#ifndef I2C_LPC_H
#define I2C_LPC_H 1

/* ----- Control register bits ----------------------------------------	*/
#define I2C_LPC_PIN	0x80
#define I2C_LPC_ESO	0x40
#define I2C_LPC_ES1	0x20
#define I2C_LPC_ES2	0x10
#define I2C_LPC_ENI	0x08

#define I2C_LPC_STO	0x40
#define I2C_LPC_ACK	0x01

/*command register*/
#define I2C_LPC_STA	0x80
#define I2C_LPC_ABT	0x40

/*status register*/
#define I2C_LPC_TBE 0x02
#define I2C_LPC_IBB 0x80
#define I2C_LPC_RBF 0x01
#define I2C_LPC_TD 0x08

#define I2C_LPC_START    I2C_LPC_STA
#define I2C_LPC_STOP     I2C_LPC_STO
#define I2C_LPC_REPSTART I2C_LPC_STA
#define I2C_LPC_IDLE     

/* ----- Status register bits -----------------------------------------	*/
/*#define I2C_LPC_PIN  0x80    as above*/

#define I2C_LPC_INI 0x40   /* 1 if not initialized */
#define I2C_LPC_STS 0x20
#define I2C_LPC_BER 0x10
#define I2C_LPC_AD0 0x08
#define I2C_LPC_LRB 0x08
#define I2C_LPC_AAS 0x04
#define I2C_LPC_LAB 0x02
#define I2C_LPC_BB  0x80

/* ----- Chip clock frequencies ---------------------------------------	*/
#define I2C_LPC_CLK3	0x00
#define I2C_LPC_CLK443	0x10
#define I2C_LPC_CLK6	0x14
#define I2C_LPC_CLK	0x18
#define I2C_LPC_CLK12	0x1c

/* ----- transmission frequencies -------------------------------------	*/
#define I2C_LPC_TRNS90 0x00	/*  90 kHz */
#define I2C_LPC_TRNS45 0x01	/*  45 kHz */
#define I2C_LPC_TRNS11 0x02	/*  11 kHz */
#define I2C_LPC_TRNS15 0x03	/* 1.5 kHz */


#define I2C_LPC_OWNADR	0
#define I2C_LPC_INTREG	I2C_LPC_ES2
#define I2C_LPC_CLKREG	I2C_LPC_ES1

#define I2C_LPC_REG_TEST 0x01
#define I2C_LPC_REG_BUS_SEL 0x80
#define I2C_LPC_REG_DEVICE_ADDR 0x81
#define I2C_LPC_REG_BYTE_COUNT 0x83
#define I2C_LPC_REG_COMMAND 0x84
#define I2C_LPC_REG_STATUS 0x85
#define I2C_LPC_REG_DATA_RX1 0x86
#define I2C_LPC_REG_DATA_RX2 0x87
#define I2C_LPC_REG_DATA_RX3 0x88
#define I2C_LPC_REG_DATA_RX4 0x89
#define I2C_LPC_REG_DATA_TX1 0x8a
#define I2C_LPC_REG_DATA_TX2 0x8b
#define I2C_LPC_REG_DATA_TX3 0x8c
#define I2C_LPC_REG_DATA_TX4 0x8d

#endif /* I2C_LPC_H */
