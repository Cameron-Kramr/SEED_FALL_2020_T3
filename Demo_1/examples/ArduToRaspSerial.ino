
void setup() {                                          // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  int data = 0;
  byte arra[2];

  if (Serial.available() > 0){                          //checks if bytes were sent
    Serial.readBytesUntil('a',arra,2);                  //reads in all the bytes
    data = (arra[0]<<8)+arra[1];                        //combines the bytes
    Serial.println(data);                               //sends data to Pi
  } 
  
}                                                       //SIDE NOTE: It seems like each "byte" is 8 bits long, which confuses me. But it works so who am I to argue.





/*
void loop() {                                           //this loop reads bytes and stores them in a character array
  char arra[5];                                         //decrares character array

  if (Serial.available() > 0){
    Serial.readBytesUntil('\n',arra,5);                 //the '\n' is the character that the function looks for in the bytes to know to stop reading

    for (int i = 0; i<5; i++){                          //this just prints the character array
      Serial.println(arra[i]);
    }
    
  }
  
}
  
*/


//
