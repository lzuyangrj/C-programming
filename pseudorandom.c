/*
 1D random number generator 
 from stackoverflow, by R. Yang (20170820)
*/

#include <stdio.h>

int random_int(int min_num, int max_num);

int main(void)
{
  srand(time(NULL));
  printf("Min : 1 Max : 40 %d\n", random_number(1,40));
  printf("Min : 100 Max : 1000 %d\n",random_number(100,1000));
  return 0;
}

int random_int(int min_num, int max_num)
{
  int result = 0, low_num = 0, hi_num = 0;

  if (min_num < max_num)
    {
      low_num = min_num;
      hi_num = max_num + 1; // include max_num in output
    } else 
    {
      low_num = max_num; // include max_num in output
      hi_num = min_num + 1;
    }

  result = (rand() % (hi_num - low_num)) + low_num;

  return result;
}
