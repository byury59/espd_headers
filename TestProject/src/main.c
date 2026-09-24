#include "main.h"

int counter;

static int add(int a, int b)
{
    return a + b;
}

void tick(void)
{
    counter = add(counter, 1);
}

int main(void)
{
    tick();
    return 0;
}
