# Rozwinięcie gry — pomysły (extra.md)

Katalog pomysłów na rozwinięcie Space Invaders (Python + Arcade 3.3.3).
Każdy punkt ma szacowany nakład: S (mały, do dnia), M (średni, kilka dni), L (duży, tydzień+).

Uwaga: projekt ma płaski layout (bez pakietów) — nowe mechaniki powinny się
mieścić w dodatkowych, pojedynczych plikach (np. `power_up.py`, `ufo.py`),
zgodnie z istniejącym stylem (`enemy_invader.py`, `enemy_bullet.py`).

---

## Faza 1 — fundamenty rozgrywki (brakujące klasyczne elementy)

1. **Zwycięstwo poziomu i kolejne poziomy** (M)
   Teraz po wymazaniu formacji nic się nie dzieje. Dodaj: wykrycie "wszyscy
   wrogowie dead" → krótki baner "LEVEL CLEAR" → `setup_level(level+1)` z
   rosnącymi parametrami: `ENEMY_SPEED`, `BULLET_SPEED`, `chance` w
   `allow_enemies_to_fire` skalowane od numeru poziomu. Nowe stałe do
   `constants.py` (np. bazowe + mnożnik po poziomie).
2. **Porażka, gdy wrogowie dotrą do dołu** (S)
   Klasyczna reguła: żywy wróg z `bottom >= ~100` (przejedzenie pancerzy) =
   game over. Sprawdzanie w pętli ruchu wrogów.
3. **UFO / statek zagadka** (M)
   Nowy sprite `ufo.py` przelatujący co ~30 s przez górę ekranu (losowy
   kierunek), punktacja 50/100/150/300 losowo. Kolizja z pociskiem gracza.
   Dźwięk "mystery" (arcade ma `:resources:sounds/`).
4. **Power-upy spadające z zabitych wrogów** (M)
   Pulel `power_up.py` (szansa ~10% przy zabójstwie):
   - podwójny strzał,
   - szybszy strzał (krótszy cooldown gracza),
   - dodatkowe życie,
   - tarcza na gracza (jednorazowy blok pocisku),
   - spowolnienie wrogów na 10 s.
   Kolizja z graczem = aktywacja + dźwięk.
5. **High score trwale zapisany** (S)
   Po game over: porównanie z rekordem zapisanym w pliku JSON (np.
   `highscore.json` w katalogu gry), baner "NEW RECORD". Ustawienie
   `high_score` w stałych + odczyt/zapis przy starcie/koncu gry.
6. **Pauza (P)** (S)
   `on_key_press` → flaga `paused`, pomijanie `process_*` i rysowanie baneru
   "PAUSED".

## Faza 2 — głębia i różnorodność

7. **Różne typy wrogów w formacji** (M)
   Wykorzystaj dostępne sprite'y Kenneya: np. dolne wiersze = "skorpiony"
   (wolniejsze, 30 pkt), górne = klasyczne. Dodatkowe klasy/pola w
   `enemy_invader.py` (`speed_factor`).
8. **Bomby homingowe wrogów** (M)
   Rzadszy pocisk (`chance` osobna), który skręca w stronę gracza
   (z ograniczoną prędkością obrotu) — klasyczna "invader bomb".
   Uwaga: nie łam invariantu "jeden pocisk = jeden kill".
9. **Nuke / bomba (klawisz B, 1× na grę lub za punkty)** (S)
   Usuwa wszystkich żywych wrogów (z animacją eksplozji — zachować regułę
   `dead` przez 0.5 s, żeby animacje się nie łamały), efekt
   ekranowy.
10. **Ekstra życie co N punktów** (S)
    Progi: 1000, 2000, 3000… baner + dźwięk.
11. **Sterowanie klawiaturą (strzałki)** (S)
    Obecnie tylko mysz. `on_key_press/on_key_release` → stałe `change_x`
    gracza; klawisz spacji / X do strzału (obok myszki).
12. **Wyłącznik dźwięku (M) i głośność w menu startowym** (S)
    `arcade.set_sound_volume(...)`, zapis preferencji do tego samego JSON
    co high score.

## Faza 3 — wygląd, polerowanie, dystrybucja

13. **Cząsteczkowe eksplozje** (M)
    `arcade.ParticleSystem` zamiast tylko sprite'u eksplozji — spójnie z
    istniejącą animacją 0.5 s.
14. **Pop-upy punktacji** (S)
    Pływający tekst "+10/+20/+30" w miejscu trafienia (nowa lekka klasa
    sprite z `update()` → `change_y` i zanikanie; pamiętaj o
    `super().update(delta_time)` — pułapka z AGENTS.md).
15. **Gwiazdy w tle / parallax** (S)
    Statyczny SpriteList malowany jako pierwszy w `on_draw` (bez kamery,
    żeby nie ruszał z world-em — albo z drugą kamerą).
16. **Screen shake po trafieniu gracza** (S)
    Krótkie losowe przesuwanie `camera.position` na ~0.3 s.
17. **Menu opcji / ekran instrukcji rozbudowany** (S)
    Lista power-upów i punktacji typów w `InstructionView`.
18. **Certyfikacja jakości: smoke test + lint** (M)
    Headless: `arcade.Window(..., visible=False)` (arcade 3.3.x) + pętla
    `GameView` na ~300 klatek bez ekscepcji; `ruff` dla flata.
    Uwaga: `GameView` powstaje dopiero po kliknięciu — w teście wołaj
    `GameView()` + `setup()` bezpośrednio.
19. **Pakowanie w PyInstaller** (L)
    Jednoplikowy wykonywalny (Linux `.AppImage`/bin, Windows `.exe`).
    Uwaga: tekstury Kenneya i fonty trzeba dodać do `--add-data`;
    ścieżki `:resources:sounds/...` działają z arkadą niezależnie.
20. **Wersja EN/PL interfejsu** (S)
    Stałe tekstów (`SCREEN_TITLE`, napisy w viewach) w jednym miejscu,
    przełącznik w menu.

---

## Rekomendowana kolejność

- **Krok 1 (Faza 1):** pkt 1 + 2 — bez nich gra "nie kończy się" po wygranej
  poziomie i brakuje klasycznego warunku przegranej.
- **Krok 2:** pkt 5 + 6 + 11 (niski nakład, duża wartość).
- **Krok 3:** pkt 3 + 4 (UFO + power-upy — największy skok "feels like
  classic arcade").
- **Krok 4+:** reszta według uznania; pkt 18 warto zrobić wcześniej niż 19,
  żeby mieć siatkę bezpieczeństwa przed packagingiem.

## Ograniczenia / pułapki (z AGENTS.md)

- Płaski layout — nowe mechaniki w pojedynczych plikach + `constants.py`.
- Arcade 3.3.3: `Sprite.update()` musi wołać `super().update()`,
  `SpriteList.clear()` w pętli → `break`, kamera `unproject` dla myszy.
- Invarianty: `enemy.dead` przez 0.5 s, "jeden pocisk = jeden kill",
  replay przez `GameView.setup()`.
- Weryfikacja zmian: uruchamianie gry (`./venv/bin/python main.py`).
