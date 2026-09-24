/* Контрольный файл: случаи, на которых исходный PPU_SHAPS.py ошибается.
   Ожидаемый результат для каждой функции указан в комментарии перед ней. */

#define MAX_SIZE 10
typedef struct { int val; int field; } MyType_t;
enum { STATE_IDLE, STATE_RUN };
struct S { int a; };

int g_counter;
int g_state;

/* ожидается: найдена; x = in; return = x */
__attribute__((aligned(16), section(".critical")))
int compute(int x) { return x; }

/* ожидается: p = out */
void fill(int *p) { *p = 42; }

/* ожидается: s = out (исходная версия: in, внешние: a) */
void setf(struct S *s) { s->a = 1; }

/* ожидается: t = in, n = in; return = r;
   external: g_counter (in), g_state (out)
   исходная версия: 8 "глобалей", из них 6 ложных */
int sum(MyType_t *t, int n)
{
    MyType_t tmp;
    int r = 0;
    tmp.field = n;
    r = t->val + MAX_SIZE + g_counter;
    g_state = STATE_IDLE;
    return (r);
}

/* ожидается: a = in (передача по значению) */
void sh(int a) { a <<= 1; }

/* ожидается: найдена (исходная версия: теряется из-за '{') */
void brace(void) { char c = '{'; (void)c; }

/* ожидается: найдена */
void after(void) { }

/* ожидается: НЕ найдена (внутри комментария)
void old(int z) {
}
*/

#if 0
/* ожидается: НЕ найдена (неактивная ветка) */
int dead(void) {
    return 0;
}
#endif

/* ожидается: return указан (исходная версия: None) */
int nonvoid(int a) { return a + 1; }
