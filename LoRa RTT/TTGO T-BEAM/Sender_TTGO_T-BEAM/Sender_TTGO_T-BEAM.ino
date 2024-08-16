#include <LoRa.h>

#define BAND 910E6  // Banda

// Definición de pines para TTGO T-BEAM
#define SCK     5    // GPIO5  -- SX127x SCK
#define MISO    19   // GPIO19 -- SX127x MISO
#define MOSI    27   // GPIO27 -- SX127x MOSI
#define SS      18   // GPIO18 -- SX127x CS
#define RST     23   // GPIO23 -- SX127x RESET
#define DI0     26   // GPIO26 -- SX127x IRQ(Interrupt Request)

String message = "";
int tamano_paquete = 0;
int rssi = 0;
float snr = 0;
long freqError = 0;
int packSize = 0;
String packet = "";
bool packetReceived = false;

void LoRa_Sender(String message);
void LoRa_Receiver();
void Serial_Receiver();
void Serial_Sender();
void ConfiguracionLoRa();

void LoRa_Sender(String message) {
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();
  while (LoRa.endPacket() == 0);
  LoRa.receive(); // Volver al modo de recepción inmediatamente
}

void LoRa_Receiver() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    packet = "";
    for (int i = 0; i < packetSize; i++) {
      packet += (char)LoRa.read();
    }
    rssi = LoRa.packetRssi();
    snr = LoRa.packetSnr();
    freqError = LoRa.packetFrequencyError();
    packetReceived = true;  // Marca que se ha recibido un paquete completo
  }
}

void Serial_Receiver() {
  if (Serial.available() > 0) {
    message = Serial.readStringUntil('\n');
    message.trim();

    // Eliminar posibles caracteres de retorno de carro '\r'
    message.replace("\r", "");

    // Calcular el tamaño del paquete
    tamano_paquete = message.length();
    
    // Enviar el mensaje por LoRa
    LoRa_Sender(message);
  }
}

void Serial_Sender() {
  if (packetReceived && packet.length() > 0) {
    Serial.println(packet);
    Serial.println(rssi);
    Serial.println(snr);
    Serial.println(freqError);
    packet = "";  // Limpiar el paquete después de enviarlo
    packetReceived = false;  // Resetea el estado después de enviar el paquete
    rssi = 0;
    snr = 0;
    freqError = 0;
    message = "";
    packSize = 0;
    tamano_paquete = 0;
  }
}

void ConfiguracionLoRa() {
  LoRa.setTxPower(20, PA_OUTPUT_PA_BOOST_PIN); // Establecer la potencia de transmisión dBm
  LoRa.setFrequency(BAND);
  LoRa.setSpreadingFactor(10);  // SF12
  LoRa.setSignalBandwidth(125E3);  // 62.5 kHz
  LoRa.setCodingRate4(8);  // 4/8
  LoRa.setPreambleLength(12);  // Longitud del preámbulo
  LoRa.setSyncWord(0x12);  // Palabra de sincronización
  LoRa.enableCrc();
}

void setup() {
  Serial.begin(115200);

  // Inicialización para TTGO T-BEAM
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DI0);

  if (!LoRa.begin(BAND)) {
    while (true);
  }

  ConfiguracionLoRa();
  LoRa.receive();  // Asegurar que el módulo esté en modo de recepción al inicio
}

void loop() {
  Serial_Receiver();
  LoRa_Receiver();
  Serial_Sender();
}
