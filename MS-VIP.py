#IMPORTACIONES--------------------------------------------------------------------------------------------------------------------------------------------------------IMPORTACIONES
from netmiko import ConnectHandler                                                                              #Modulo de conexion
import json                                                                                                     #Modulo para volver una tupla los comandos
ciclo = 1                                                                                                       #Contador del ciclo de ejecucion
#ENTRADA DE DATOS--------------------------------------------------------------------------------------------------------------------------------------------------ENTRADA DE DATOS
objetivo = input("Mac: ")                                                                                       #Mac objetivo
objetivo = list((objetivo.lower()).replace("-",""))                                                             #Remplazo de caracteres inecesarios y en minusculas
objetivo.insert(4,".")                                                                                          #insercion de puntos al formato de la MAC
objetivo.insert(9,".")
objetivo = "".join(objetivo)                                                                                    #Convercion de lista a texto
#CREDENCIALES SSH--------------------------------------------------------------------------------------------------------------------------------------------------CREDENCIALES SSH                                                                                                                
switch = input("\nIP switch: ")                                                                                 #Ip del switch a conectar vía SSH
user = input("Usuario: ")                                                                                       #Usuario SSH
u_pass = input("Contraseña: ")                                                                                  #Contraseña SSH
#CONEXION SSH----------------------------------------------------------------------------------------------------------------------------------------------------------CONEXION SSH
Device = {"host": switch, "username": user, "password": u_pass, "device_type": "cisco_ios", "secret": "cisco"}  #Se añaden las credenciales en una variable
Connect_Device = ConnectHandler(**Device)             
Connect_Device.enable()                                                                                         #Conexion con credenciales de la variable
#CICLO DE EJECUCION----------------------------------------------------------------------------------------------------------------------------------------------CICLO DE EJECUCION
while ciclo == 1:
    mac_table = Connect_Device.send_command("show mac address-table",use_textfsm = True)                        #Comando mac address-table
    mac_table = (json.dumps(mac_table, indent = 2))
    mac_table = json.loads(mac_table)                                                                           #conversion a Json
    
    cdp = Connect_Device.send_command("show cdp neighbors detail",use_textfsm = True)                           #Comando sh cdp neighbor detail
    cdp = (json.dumps(cdp, indent = 2))
    cdp = json.loads(cdp)                                                                                       #conversion a Json

    output_run = Connect_Device.send_command("show run | include hostname")                                     #Comando sh run | include hostname
    try:#BUSQUEDA DE VECINOS------------------------------------------------------------------------------------------------------------------------------------BUSQUEDA DE VECINOS
        for sw  in range(len(cdp)):
            puertov = (cdp[sw]["local_port"])                                                                   #Obtencion del puerto cdp

        if "G" in puertov:                                                                                      #Formateo puerto FastEthernet
            puertov=(puertov[0:2])+(puertov[15:])
        else:
            puertov=(puertov[0:2])+(puertov[12:])                                                               #Formateo puerto GigabitEthernet
        (cdp[sw]["local_port"])=puertov

    except:                                                                                                     #Error en el formateo de puertos
        print("Error - puertos cdp")
    try:#COMPARACION DE LA MAC BUSCADA----------------------------------------------------------------------------------------------------------------COMPARACION DE LA MAC BUSCADA
        for mac in range(len(mac_table)):
            if objetivo == (mac_table[mac]['destination_address']):                                             #Comparacion mac objetivo con macs en switch
                puerto_mac = (mac_table[mac]['destination_port'][0])                                            #Obtencion puerto donde se encuentra mac objetivo
            else: pass                                                                                          #La MAC en este puesto no coincide con la buscada
        
        for vecino in range(len(cdp)):
            puerto_v = (cdp[vecino]["local_port"])                                                              #Obtencion puerto vecino
            ip_ssh = (cdp[vecino]["management_ip"])                                                             #Obtencion ip vecino para conexion SSH

            try:
                if puerto_v == puerto_mac:                                                                      #Busqueda de coincidencias puerto vecino/mac
                    Device["host"]=ip_ssh                                                                       #Se cambia la ip en el diccionario de credenciales
                    Connect_Device.enable()                                                                     #Conexion con credenciales de la variable
                else:                                                                                           #Resultado positivo de la busqueda de MAC
                    print(f'''\nMac: {objetivo}\nConectado al puerto: {puerto_mac}\nSwitch: {output_run}\n''')
                    ciclo = 0                                                                                   #Se para la ejecucion
                    break
            except:                                                                                             #Resultado negativo de la busqueda de MAC 
                print(f'''\nMac: {objetivo}\nNo encontrada\n''')
                ciclo = 0                                                                                       #Se para la ejecucion
                break
    except:                                                                                                     #Error en la conexion con siguiente switch
        print("Error - conexion/mac")