#include <stdio.h>
#include <unistd.h>
int main(int agrc, char **argv){
    int x=0, i=0;
    for(i=0;i<3;i++){
        fork();
        x=x+5;
    }
    printf("x = %d\n", x);
    return 0;
}