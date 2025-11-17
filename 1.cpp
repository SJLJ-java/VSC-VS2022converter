// Windchill chart 
#include <iostream>
#include <string>
#include <math.h>
#include <iomanip>
int main(){
    int windChill[11];
    int temperature[9];
    std::string temperatureS;
    double total;
    std::cout << "    ";
    // Set up 11 numbers, starting at 0 and incrementing by 5
    for(int i=0;i<11;i++){
        windChill[i] = 5*i;
        std::cout << std::setw(5) << windChill[i];
    }
    // Newline I have dubbed Jerry
    std::cout << "\n    "/*<-Jerry*/;
    for(int i=0;i<56;i++){
        std::cout << "-";
    }
    // Set up 9 numbers, starting at -20 and incrementing by 10
    for(int i=-20;i<9;i++){
        temperature[i] = 10*i;
        temperatureS = std::to_string(temperature[i]);
        // Rude newline that doesn't deserve a name
        std::cout << "\n"/*<-Rude*/ << std::setw(3) << temperatureS << "|";
        for(int a=0;a<11;a++){
            if(a==0){
                // Don't use the formula if there is no wind
                total = temperature[i];
            }
            else{
                // Calculate temperature
                total = 35.74 + 0.6215 * temperature[i]- 35.75 * 
                pow(windChill[a], 0.16) + 0.4275 
                * temperature[i] * pow(windChill[a], 0.16);
            }
            std::cout << std::setw(5) << round(total);
        }
    }
    // Newline I have dubbed Steve
    std::cout << "\n"/*<-steve*/;
}