import farm_game.swi
import farm_game.server


import sys
def main():
    port = int(sys.argv[1]) if len(sys.argv)>1 else 8080
    addr = ''
    farm_game.swi.browser(port)
    farm_game.swi.start(farm_game.server.Server, port, addr=addr)

if __name__ == '__main__':
    main()
