from var import *
import logging
import logging.config


class Frame:
    def __init__(self, data_hex):
        self.data_convert_to_str(data_hex)
        self.identifier_str = self.data_str[
                            STRUC_COMMAND_MESSAGE['identifier_message'][0]*2:
                            STRUC_COMMAND_MESSAGE['identifier_message'][0]*2 +
                            STRUC_COMMAND_MESSAGE['identifier_message'][1]*2]
        self.command_str = self.data_str[
                            STRUC_COMMAND_MESSAGE['identifier_command'][0]*2:
                            STRUC_COMMAND_MESSAGE['identifier_command'][0]*2 +
                            STRUC_COMMAND_MESSAGE['identifier_command'][1]*2]

    def identifier_check(self):
        '''
        @brief    Метод проверки идентификатора посылки
        @return   Возвращает булевый результат проверки
        @detailed Сравнивает идентификатор посылки с установленным
        '''
        return self.identifier_str == STR_IDENTIFIER_COMMAND.lower()

    def command_check(self):
        '''
        @brief    Метод проверки команды посылки
        @return   Возвращает булевый результат проверки
        @detailed Сравнивает код команды посылки с доступными командами
        '''
        return self.command_str in VALUE_LEN_COMMAND

    def data_convert_to_str(self, data_hex):
        '''
        @brief    Метод преобразования данных посылки в строку
        @param    data_hex данные посылки
        @type     data_hex hex
        @return   Преобразованные в строку данные посылки
        @detailed Преобразовывает hex в str отбросив первые 2 символа
                  прификса шестнадцатеричных типов данных
        '''
        self.data_str = data_hex.hex()

    def len_calculation(self):
        '''
        @brief    Метод подсчета длины посылки
        @return   Длину посылки в байтах
        @detailed Считает количество символов в строке данных и делит на 2,
                  так как на 1 байт приходится 2 символа
        '''
        logging.config.dictConfig(dictLogConfigZorkii)
        logger = logging.getLogger('zorkiiApp.len_calculation')
        logger.debug(self.data_str)
        logger.debug('len fact {}'.format(len(self.data_str) / 2))
        return len(self.data_str) / 2

    def len_check(self):
        '''
        @brief    Метод проверки длины посылки
        @return   Возвращает булевый результат проверки
        @detailed Проверяет длину посылки учитывая параметры команды.
                  Стандартный размер структурного блока равен 18 байт
                  плюс параметры команды.
        '''
        logging.config.dictConfig(dictLogConfigZorkii)
        logger = logging.getLogger('zorkiiApp.len_check')
        logger.debug('Wait len {} {}'.format((
                     VALUE_LEN_COMMAND[self.command_str]),
                     (STRUC_COMMAND_MESSAGE['param'])))
        return (self.len_calculation() ==
                (VALUE_LEN_COMMAND[self.command_str] +
                 STRUC_COMMAND_MESSAGE['param']))

    def command_attribute_check(self):
        '''
        @brief    Метод проверки атрибутов команды посылки
        @return   Возвращает булевый результат проверки
        @detailed Проверяет корректность атрибутов для данной команды.
                  Если пришла команда изменить значение диафрагмы
                  (STR_COMMAND_APERTURES), проверяем значение направления;
                  Если пришла команда установить время ЦТК
                  (STR_COMMAND_SET_TIME) проверяет значение года, месяца,
                  дня, часа, минут и секунд, при этом количество лет
                  ограниченно 100.
        '''
        if self.command_str == STR_COMMAND_APERTURES:
            return int(self.data_str[STRUC_COMMAND_MESSAGE['param']*2:
                                     STRUC_COMMAND_MESSAGE['param']*2 +
                                     VALUE_LEN_COMMAND[self.command_str] * 2 -
                                     2], 16) < 2
        elif self.command_str == STR_COMMAND_SET_TIME:
            return (int(self.data_str[36:38], 16) < 100) and \
                    (0 < int(self.data_str[38:40], 16) < 13) and \
                    (0 < int(self.data_str[40:42], 16) < 32) and \
                    (int(self.data_str[44:46], 16) < 24) and \
                    (int(self.data_str[46:48], 16) < 60) and \
                    (int(self.data_str[48:50], 16) < 60)
        else:
            return True
