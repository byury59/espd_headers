/* Модуль с комментариями в свободной форме перед функциями.
   Нужен для проверки переноса старого описания в графу Note. */

/* Сбрасывает буфер приёма */
void rx_reset(unsigned char *buf, int len)
{
    int i;
    for (i = 0; i < len; i++) {
        buf[i] = 0;
    }
}

// Возвращает контрольную сумму
// буфера длиной len
unsigned char checksum(const unsigned char *buf, int len)
{
    unsigned char s = 0;
    int i;
    for (i = 0; i < len; i++) {
        s += buf[i];
    }
    return s;
}
