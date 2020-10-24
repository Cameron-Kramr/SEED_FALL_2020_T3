
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




//
