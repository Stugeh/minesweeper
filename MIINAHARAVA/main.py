"""
Miinaharavan päämoduuli, joka suorittaa ohjelman logiikan haravaston avulla.

GAME-sanakirjaan tallennetaan pelin tämänhetkinen tila.
    board: kaksiulotteinen lista, joka kuvaa mitä näytöllä näkyy.
    original: kaksiulotteinen lista, joka pitää muistissa missä miinat ovat.
    checked: open_tiles-funktion tarkistamat ruudut. Tarvitaan loputtomien looppien välttämiseksi.
    mines: miinojen lukumäärä.
    seconds: kulunut aika sekunteina
    time: kulunut aika samassa muodossa, kuin se näkyy käyttäjälle.
    moves: siirtojen määrä.
    gameover: Boolean arvo joka on True kun peli päättyy.
    win: Boolean arvo, joka on True kun käyttäjä voittaa
"""

import random
import copy
from time import asctime
import haravasto as har

GAME = {
    "board": [],
    "original": [],
    "checked": [],
    "mines": 0,
    "seconds": 0,
    "time": '00:00',
    "moves": 0,
    "gameover": False,
    "win": False
}

SPRITE_WIDTH = 40


def reset_dictionary():
    """
    Nollaa GAME-sanakirjan pelin alussa, että edellinen peli ei häiritse uutta peliä.
    """
    GAME["gameover"] = False
    GAME["win"] = False
    GAME["time"] = '00:00'
    GAME["seconds"] = 0
    GAME["board"] = []
    GAME["original"] = []
    GAME["checked"] = []
    GAME["moves"] = 0


def print_scores():
    """
    Käyttäjän halutessa voidaan tulostaa High-Score lista tiedostosta
    """
    try:
        print("****************")
        with open("highscores.txt", 'r') as tied:
            for line in tied:
                print(line.rstrip())
    except FileNotFoundError:
        print("Ei highscoreja")


def game_over():
    """
    Jos pelaaja on hävinnyt suljetaan peli-ikkuna ja palataan valikkoon, jos taas voitetaan
    tulos tallennetaan, peli-ikkuna suljetaan ja palataan valikkoon
    """
    if GAME["gameover"]:
        har.lopeta()
    if GAME["win"]:
        grid = "{}x{}".format(len(GAME["board"][0]), len(GAME["board"]))
        highscore = "Päivämäärä: {} \nAika: {} \nSiirrot: {} \nRuudukko: {} \nmiinat:  {}\n".format(
            asctime(), GAME["time"], GAME["moves"], grid, GAME["mines"])
        with open("highscores.txt", 'a') as tied:
            tied.write(highscore)
            tied.write('****************\n')
        har.lopeta()


def keyboard_handler(symbol, mod):
    """
    pelin ollessa ohi "press any key to continue" tyyppinen homma.
    """
    if GAME["gameover"] or GAME["win"]:
        game_over()


def timer(elapsed):
    """
    Ottaa aikaa pelin ollessa käynnissä
    """
    if not GAME["gameover"] and not GAME["win"]:
        GAME["seconds"] += 1
        mins = GAME["seconds"] // 60
        sec = GAME["seconds"] % 60
        GAME["time"] = "{:02}:{:02}".format(mins, sec)


def draw_board():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """

    har.tyhjaa_ikkuna()
    har.piirra_tausta()
    if GAME["gameover"]:
        har.piirra_tekstia("hävisit :(", 150, len(GAME["board"])*SPRITE_WIDTH, (150, 40, 27, 255))
    if GAME["win"]:
        har.piirra_tekstia("VOITIT!!! :)", 150, len(GAME["board"])*SPRITE_WIDTH, (0, 230, 64, 255))
    har.piirra_tekstia(GAME["time"], 10, len(GAME["board"])*SPRITE_WIDTH)
    har.aloita_ruutujen_piirto()
    for i, _y_ in enumerate(GAME["board"]):
        for j, _x_ in enumerate(GAME["board"][i]):
            if _x_ != 'x':
                har.lisaa_piirrettava_ruutu(_x_, j*SPRITE_WIDTH, i*SPRITE_WIDTH)
            elif not GAME["gameover"]:
                har.lisaa_piirrettava_ruutu(' ', j*SPRITE_WIDTH, i*SPRITE_WIDTH)
            else:
                har.lisaa_piirrettava_ruutu('x', j * SPRITE_WIDTH, i * SPRITE_WIDTH)
    har.piirra_ruudut()
    if GAME["gameover"] or GAME["win"]:
        center_horizontal = len(GAME["board"][0]) * SPRITE_WIDTH // 2
        center_vertical = len(GAME["board"]) * SPRITE_WIDTH // 2
        if GAME["gameover"]:
            har.piirra_tekstia("Paina mitä vain", center_horizontal-147, center_vertical, (150, 40, 27, 255))
        elif GAME["win"]:
            har.piirra_tekstia("Paina mitä vain", center_horizontal-147, center_vertical, (0, 230, 64, 255))


def open_tiles(x, y):
    """
    Saa mouse_handler-funktiolta koordinaatit ja avaa tuntemattomat ruudut kunnes törmää miinoihin.
    """
    board = GAME["board"]
    x = int(x / SPRITE_WIDTH)
    y = int(y / SPRITE_WIDTH)
    if board[y][x] == ' ':
        GAME["moves"] += 1
        handling = [(x, y)]
        buffer = []
        while handling:
            x, y = handling.pop(-1)
            GAME["checked"].append((x, y))
            mines = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    y_offset = y + i
                    x_offset = x + j
                    if len(board) > y_offset >= 0 and len(board[0]) > x_offset >= 0:
                        if (x_offset, y_offset) not in handling and (x_offset, y_offset) not in GAME["checked"]:
                            buffer.append((x_offset, y_offset))
                        if GAME["original"][y_offset][x_offset] == 'x':
                            mines += 1
            if board[y][x] == ' ':
                board[y][x] = str(mines)
            if mines == 0:
                for buf_x, buf_y in buffer:
                    if (buf_x, buf_y) not in GAME["checked"]:
                        handling.append((buf_x, buf_y))
            buffer.clear()
    elif board[y][x] == 'x':
        GAME["gameover"] = True


def mouse_handler(_x_, _y_, mouse_button, muokkaus):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    Käskee toista funktiota laskemaan ruudun ja avaamaan sen jos vasenta painiketta painetaan.
    Oikealla painikkeella lisätään lippu laudalle.
    """
    if not GAME["gameover"] and not GAME["win"]:
        if _x_ < len(GAME["board"][0]) * SPRITE_WIDTH and _y_ < len(GAME["board"]) * SPRITE_WIDTH:
            if mouse_button == har.HIIRI_VASEN:
                open_tiles(_x_, _y_)
            elif mouse_button == har.HIIRI_OIKEA:
                if GAME["board"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] in (' ', 'x'):
                    GAME["board"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] = 'f'
                    GAME["moves"] += 1
                elif GAME["board"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] == 'f':
                    if GAME["original"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] == ' ':
                        GAME["board"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] = ' '
                    elif GAME["original"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] == 'x':
                        GAME["board"][int(_y_ / SPRITE_WIDTH)][int(_x_ / SPRITE_WIDTH)] = 'x'
                    GAME["moves"] += 1
            unopened_count = sum(space.count(' ') for space in GAME["board"])
            mines_left = sum(x.count('x')for x in GAME["board"])
            mines_original = sum(x.count('x')for x in GAME["original"])
            flags = sum(f.count('f')for f in GAME["board"])
            if mines_left + flags == mines_original and unopened_count == 0:
                GAME["win"] = True


def start():
    """
    lataa grafiikat, asettaa kasittelijat ja avaa peli-ikkunan
    """
    har.lataa_kuvat("spritet")
    har.luo_ikkuna(len(GAME["board"][0]*SPRITE_WIDTH), len(GAME["board"])*SPRITE_WIDTH+50, (255, 255, 255, 200))
    har.aseta_hiiri_kasittelija(mouse_handler)
    har.aseta_nappain_kasittelija(keyboard_handler)
    har.aseta_piirto_kasittelija(draw_board)
    har.aseta_toistuva_kasittelija(timer, 1)
    har.aloita()


def set_mines(board, safe, mines):
    """
    Asettaa kentällä N kpl miinoja satunnaisiin paikkoihin. ja ottaa kopion muokkaamattomasta kentasta.
    """
    for n__ in range(mines):
        while True:
            x_x = random.randint(0, len(board[0])-1)
            y_y = random.randint(0, len(board)-1)
            if (x_x, y_y) in safe:
                board[y_y][x_x] = 'x'
                safe.remove((x_x, y_y))
                GAME["original"] = board
                break
    GAME["board"] = copy.deepcopy(GAME["original"])


def board_create(lines=10, collumns=10, mines=15):
    """
    luo tyhjan pelikentan ja kutsuu "set_mines"-funktiota miinoittamaan sen.
    """
    GAME["mines"] = mines
    board = []
    for line in range(lines):
        board.append([])
        for col in range(collumns):
            board[-1].append(" ")
    GAME["original"] = board
    left = []
    for x in range(collumns):
        for y in range(lines):
            left.append((x, y))
    set_mines(GAME["original"], left, mines)


def new_custom_game():
    """
    kysyy kayttäjälta kentän tiedot ja välittaa ne board_create-funktiolle
    """
    while True:
        try:
            collumns = int(input("\nRuudukon leveys: \n>>"))
            lines = int(input("Ruudukon korkeus: \n>>"))
            mines = int(input("Miinojen lukumaara: \n>>"))
            board_create(lines, collumns, mines)
            break
        except ValueError:
            print("Yritäpä uusiksi.")


if __name__ == '__main__':
    while True:
        reset_dictionary()
        selection = input("1) Helppo peli\n2) Keskivaikea peli\n3) vaikea peli\n4) Custom peli\n"
                          "H) Highscores\nQ) Quit\n>>").lower()
        if selection == '1':
            board_create(9, 9, 10)
            start()
        elif selection == '2':
            board_create(16, 16, 40)
            start()
        elif selection == '3':
            board_create(16, 30, 99)
            start()
        elif selection == '4':
            new_custom_game()
            start()
        elif selection == 'h':
            print_scores()
        elif selection == 'q':
            break
        else:
            print("Virheellinen syöte yritä uudelleen.\n")
            continue
