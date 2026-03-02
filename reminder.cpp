// reminder.cpp
#include <iostream>
using namespace std;

int main(int argc, char* argv[]) {
    if (argc == 3) {
        cout << "💊 Reminder: Take " << argv[1] << " at " << argv[2] << endl;
    } else {
        cout << "Invalid reminder format!" << endl;
    }
    return 0;
}

