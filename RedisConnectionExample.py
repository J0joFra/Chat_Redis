import redis


if __name__ == '__main__':

    redis = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

    scelta = None
    while(scelta != "e"):
        print("")
        print("=========================")
        print("rek - Redis / Chiavi")
        print("-------------------------")
        print("ruc - Rubrica / Contatto")
        print("ru  - Rubrica")
        print("-------------------------")
        print("chi - Chiamata / Ingresso")
        print("chu - Chiamata / Uscita")
        print("-------------------------")
        print("e - esci")
        scelta = input("> ")

        if(scelta == "ruc"):
            numero = input("Numero >")
            nominativo = input("Nominativo >")
            redis.set("rubrica:" + numero + ":nominativo", nominativo)

        elif(scelta == "ru"):
            print("Rubrica =================>")
            for key in redis.scan_iter("rubrica:*:nominativo"):
                value = redis.get(key)
                print( f"{key} = {value}" )
            print("<================= Rubrica ")

        elif (scelta == "chi"):
            numero = input("Numero in ingresso >")
            value = redis.incr( "ingresso:" + numero + ":conteggio")

        elif (scelta == "chu"):
            numero = input("Numero chiamato >")
            value = redis.incr( "uscita:" + numero + ":conteggio")

        elif(scelta == "rek"):
            for key in redis.scan_iter("*"):
                value = redis.get(key)
                print( f"{key} = {value}" )
        
        
        
        
        
        
        
        






