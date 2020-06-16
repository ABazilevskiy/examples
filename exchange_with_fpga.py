'''
Протокол взаимодействия между модулем Салют и NIOS.
'''

import time
import spidev


WRITE_FLAG = 0x80
READ_FLAG = 0x7F
BASE_INTERVAL_FRAME = 1
BASE_INTERVAL_MECHANIZM = 5
FREQUENCY = 100000

SPI_DICT = {'frame_management': 0x00,
            'stop_frame': 0x00,
            'start_frame': 0x01,
            'filter_management': 0x01,
            'removing_filter': 0x00,
            'installation_filter': 0x01,
            'heated_managment': 0x02,
            'heated_off': 0x00,
            'heated_on': 0x01,
            'hdr_managment': 0x03,
            'hdr_off': 0x00,
            'hdr_on': 0x01,
            'apertures_managment': 0x04,
            'exposition_managment': 0x06,
            'interval_managment': 0x08,
            'temperature_matrix_info': 0x10,
            'temperature_cupola_info': 0x12
            }


class Exchange_using_spi(spidev.SpiDev, Exchange):

    def add_crc(self, output_message):
        '''
        @brief    Метод считает контрольную сумму посылки.
        @param    output_message массив сообщение.
        @type     output_message массив (array).
        @return   Возвращает CRC сообщения.
        @detailed Считает контрольную сумму посылки при помощи
                   "исключительного или" + 1.
        '''
        crc = 0
        for byte in output_message:
            crc = crc ^ byte
        crc += 1
        return hex(crc)

    def control_crc(self, message):
        '''
        @brief    Метод проверяет контрольную сумму посылки.
        @param    message массив сообщение.
        @type     message массив (array).
        @return   Возвращает булевы значения.
        @detailed Считает контрольную сумму посылки при помощи
                   "исключительного или" + 1 и сравнивает с
                   последним байтом посылки.
        '''
        crc = 0
        for byte in message[:-1]:
            crc = crc ^ byte
        crc += 1
        return (hex(crc) == message[:-1])

    def send_command(self, command, interval, *param):
        '''
        @brief    Отправляем команду по SPI.
        @param    message массив сообщение
        @type     message массив (array)
        @return   Возвращает результат выполнения
        @detailed Пытается 5 раз выполнить команду, проверяя ответный пакет.
                   Если попытка обмена удалась, возвращает результат. Если
                   ошибка обмена возвращает 0х03. Если ошибка SPI возвращает
                   0х01. Если отказ исполняющего механизма возвращает 0x04.
        '''
        output_message_command = [command | WRITE_FLAG, len([*param]), *param]
        output_message.append(add_crc(output_message_command))
        output_message_command = list(map(hex, output_message_command))
        try:
            for try_command in range(5):
                input_message = self.xfer(output_message_command, FREQUENCY)
                if control_crc(input_message):
                    time.sleep(interval)
                    output_message_stat = [command & READ_FLAG, len([*param]),
                                           *param]
                    output_message_stat.append(add_crc(output_message_stat))
                    output_message_stat = list(map(hex, output_message_stat))
                    input_message = self.xfer(output_message_stat, FREQUENCY)
                    if control_crc(input_message):
                        if (input_message[2]) == 0x80:
                            return False, [0x04]
                        elif ((command == SPI_DICT['apertures_managment']) and
                              (input_message[2] == 0)):
                            return True, [input_message[2]]
                        elif input_message[2:-1] == output_message_stat[2:-1]:
                            return True, [input_message[2]]
                time.sleep(interval)
            return False, [0x03]
        except:
            return False, [0x01]

    def command(self, command, *param, command_stop_frame=True,
                interval_frame=BASE_INTERVAL_FRAME,
                interval_mechanism=base_interval_mechanism):
        '''
        @brief    Основной метод выполнения команды.
        @param    command команда,
                  *param параметры,
                  command_stop_frame необходимость остановки съемки.
        @type     command hex,
                  *param hex,
                  command_stop_frame boolean.
        @return   Возвращает результат выполнения и параметры.
        @detailed Останавливает съемку при необходимости, вызывает метод
                   на формирование и отправку сообщения по SPI. Если
                   необходимо было остановить съемку для выполнения
                   команды, но съемка не была остановлена возвращает 0x02.
        '''
        if command_stop_frame:
            if not send_command(SPI_DICT['frame_management'],
                                interval_frame,
                                SPI_DICT['stop_frame']):
                return False, [0x02]
        return send_command(command, interval_mechanism, *param)

    def request(self,  command,  *param):
        '''
        @brief    Основной метод выполнения запроса.
        @param    command команда,
                  *param параметры.
        @type     command hex,
                  *param hex.
        @return   Возвращает результат выполнения и данные запроса.
        @detailed Вызывает метод на формирование и отправку запроса по SPI.
        '''
        output_message = [command & READ_FLAG, len([*param]), *param]
        output_message.append(add_crc(output_message))
        output_message = list(map(hex, output_message))
        try:
            for try_command in range(5):
                input_message = self.xfer(output_message, FREQUENCY)
                if control_crc(input_message):
                    return True, input_message
            return False, [0x03]
        except:
            return False, [0x01]
