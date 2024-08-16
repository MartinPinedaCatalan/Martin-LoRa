#include <LoRa.h>

#define BAND 910E6  // Banda

// Definición de pines para TTGO T-BEAM
#define SCK     5    // GPIO5  -- SX127x SCK
#define MISO    19   // GPIO19 -- SX127x MISO
#define MOSI    27   // GPIO27 -- SX127x MOSI
#define SS      18   // GPIO18 -- SX127x CS
#define RST     23   // GPIO23 -- SX127x RESET
#define DI0     26   // GPIO26 -- SX127x IRQ(Interrupt Request)

int rssi = 0;
int packSize = 0;
String packet = "";
bool messageReceived = false;

void LoRa_Sender(String packet);
void LoRa_Receiver();
void resetLoRa();
void ConfiguracionLoRa();

void LoRa_Sender(String packet) {
  LoRa.beginPacket();
  LoRa.print(packet);
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
    messageReceived = true;  // Marca que se ha recibido un mensaje correctamente

    // Si el paquete recibido es "", reiniciar la modulación LoRa
    if (packet == "") {
      resetLoRa();
    }
  }
}

void resetLoRa() {
  // Función para reiniciar el módulo LoRa
  LoRa.end();
  delay(1000);
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DI0);

  if (!LoRa.begin(BAND)) {
    while (true);
  }

  ConfiguracionLoRa();
}

void ConfiguracionLoRa() {
  LoRa.setTxPower(20, PA_OUTPUT_PA_BOOST_PIN);
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
  LoRa_Receiver();

  if (messageReceived) {
    LoRa_Sender(packet);
    messageReceived = false;
    packet = "";
    rssi = 0;
    packSize = 0;
  }
}
