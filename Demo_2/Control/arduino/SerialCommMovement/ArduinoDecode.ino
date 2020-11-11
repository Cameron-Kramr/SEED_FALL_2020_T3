int index = 0;
char space[1] = {' '};                                    //needed so the program knows to split up input string whenever a space occurs
char stringInput[30];                                     //the char array that the input string is placed in
String tooken[5];                                         //5 commands per string sent
float RFloat;                                             //dummy global variables
float OFloat;
float TFloat;
float VFloat;

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  //delay(100);
  decodeString();
}

void decodeString(){
  if (Serial.available() > 0){
    Serial.readBytesUntil('@',stringInput,30);                      //the "@" is arbitrary, only reads in 30 characters
    tooken[index] = strtok(stringInput, space);                     //this splits off a chunk of the input string (until the first ' ') and puts it in a string array
    Serial.println(tooken[index]);                                  //echoes the first command string 
    
    switch (tooken[index][0]){                                      //chooses which variable to set based on first character of the current string
        case 'R':
          tooken[index].setCharAt(0,'0');                           //sets the first character to a zero so only the float is left
          RFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
          Serial.print("RFloat ");
          Serial.println(RFloat);
          break;

        case 'O':
          tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
          OFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
          Serial.print("OFloat ");
          Serial.println(OFloat);
          break;
        
        case 'T':
          tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
          TFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
          Serial.print("TFloat ");
          Serial.println(TFloat);
          break;
        
        case 'V':
          tooken[index].setCharAt(0,'0');                         //sets the first character to a zero so only the float is left
          VFloat = tooken[index].toFloat();                       //sets corresponding global variable to the float determined
          Serial.print("VFloat ");
          Serial.println(VFloat);
          break;
        
        case 'C':
          Serial.println("Other command not in code yet.");
          break;
          
        default:
          Serial.println("I dont know this character.");
    }

    while (index < 5){                                                //This will loop the same things as above, but for each other commands in the input string
      if (tooken[index] != NULL){                                     //checks if there are more command strings left
        index++;
        tooken[index] = strtok(NULL,space);                           //splits off another chunk of the input string (another command)
        Serial.println(tooken[index]);                                //echoes the first command string
        
        switch (tooken[index][0]){
          case 'R':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
            RFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
            Serial.print("RFloat");
            Serial.println(RFloat);
            break;

          case 'O':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
            OFloat = tooken[index].toFloat();                        //sets corresponding global variable to the float determined
            Serial.print("OFloat ");
            Serial.println(OFloat);
            break;
        
          case 'T':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is leftleft
            TFloat = tooken[index].toFloat();                        //sets corresponding global variable to the float determined
            Serial.print("TFloat ");
            Serial.println(TFloat);
            break;
        
          case 'V':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
            VFloat = tooken[index].toFloat();                        //sets corresponding global variable to the float determined
            Serial.print("VFloat ");
            Serial.println(VFloat);
            break;
        
          case 'C':
            Serial.println("Other command not in code yet.");         //this is incase anyone wants to create a new command
            break;
          
          default:
            Serial.println("I dont know this character.");            //If it doesn't recognize the first character
        }
      }
      
      else {
        //Serial.println(index);
        index = 5;                                                    //breaks out of the while loop
        //Serial.println("It was NULL.");
      }
    }
    
    index = 0;
    while (index<5){                                                        //clears the tookens that hold each string inputed
      tooken[index] = "";
      index++;
    }
    
    index = 0;
    for (int i=0; i<30; i++){                                               //clears the stringInput array
      stringInput[i] = 0;
    }
  }
}

    /*while(tokens != NULL){
      //Serial.println(tokens);
      //tokens = strtok(NULL, space);
    //}
    token1 = tokens;
    Serial.println(token1);
    Serial.println(token1[0]);
    if (token1 != NULL){
      token2 = strtok(NULL,space);
      Serial.println(token2);
    }
    if (token2 != NULL){
      token3 = strtok(NULL,space);
      Serial.println(token3);
    }
    if (token3 != NULL){
      token4 = strtok(NULL,space);
      Serial.println(token4);
    }
    if (token4 != NULL){
      token5 = strtok(NULL,space);
      Serial.println(token5);
    }
*/
/*
  if (Serial.available() > 0){
    Serial.readBytesUntil(32,command,1);

    switch (command[0]){
      case 'R':
        Serial.readBytesUntil(32,floout,15);
        
        break;

      case 'O':
        Serial.readBytesUntil(32,floout,15);
        break;
        
      case 'T':
        Serial.readBytesUntil(32,floout,15);
        break;
        
      case 'V':
        Serial.readBytesUntil(32,floout,15);
        break;
        
      case 'C':
        Serial.readBytesUntil(32,floout,15);
        break;
        
    }
   
  }
 */

/*
void testing() {
  if (Serial.available() > 0){
    //Serial.readBytesUntil(32,arra,30);

    for (int i = 0; i<10; i++){
      Serial.println(arra[i]);
      arra[i] = 0;
    }
  }

  
}
*/
