# Przegląd kodu Space Invaders — lista błędów i problemów zgodności z Arcadą

- **Data przeglądu:** 2026-10-30
- **Środowisko:** Python 3.14, `arcade 3.3.3`, `pyglet 2.1.19` (z wirtualnego środowiska `venv/`)
- **Metoda:** analiza źródła instalowanej biblioteki arcade 3.3.3 + empiryczne testy runtime (`./venv/bin/python`)
- **Status (stan na 2026-10-30):** naprawione **wszystkie pozycje (E1–E13)** — brak otwartych błędów.

## Podsumowanie

| # | Powaga | Plik | Opis | Status |
|---|--------|------|------|--------|
| E1 | **KRYTYCZNY** | `enemy_bullet.py:16` | Pociski wrogów nie poruszają się wcale (brak `super().update()`) | ✅ naprawiono |
| E2 | **KRYTYCZNY** | `game_view.py:366-397` | `clear()` nie zatrzymuje pętli `for` → utrata wielu żyć w jednej klatce | ✅ naprawiono |
| E3 | LOGIKA | `game_view.py:304-328` | Martwe (wybuchające) wrogowie są poruszane i wywołują odwrócenie formacji | ✅ naprawiono |
| E4 | LOGIKA | `game_view.py:330-364` | Strzela górny, a nie dolny wróg kolumny; szansa liczy trupy | ✅ naprawiono |
| E5 | LOGIKA | `game_view.py:399-433` | Jeden pocisk zabija kilku wrogów (podwójny/trzykrotny wynik) | ✅ naprawiono |
| E6 | LOGIKA | `game_view.py:444` + `:369` | Pociski wrogów aktualizowane dwukrotnie w klatce | ✅ naprawiono |
| E7 | ZGODNOŚĆ 3.x | `game_view.py:223-238` | Kamera zniekształca obraz przy zmienionym oknie (brak letterboxa mimo komentarza) | ✅ naprawiono |
| E8 | ZGODNOŚĆ 3.x | `game_view.py:260-271` | Surowe współrzędne myszy traktowane jako współrzędne świata | ✅ naprawiono |
| E9 | ZGODNOŚĆ 3.x | `game_view.py:189,199,210,219` | Czcionka „Kenney Rocket" nigdy nie jest wczytywana (cicha substytucja) | ✅ naprawiono |
| E10 | MINOR | `game_view.py:267` | Martwa linia (nadpisana w `:271`) | ✅ naprawiono (efekt E8) |
| E11 | MINOR | `game_view.py:285-297`, `instruction_view.py:20-26` | Dowolny przycisk myszy strzela / startuje grę | ✅ naprawiono |
| E12 | MINOR | `game_view.py:278-283` | Gracz może wysunąć się ~33 px poza krawędź ekranu | ✅ naprawiono |
| E13 | **KRYTYCZNY** | `game_view.py:64,65,236,238` | `Rect(0,0,w,h)` i `Point2(...)` nie istnieją w 3.3.3 → crash konstrukcji `GameView` (gra nie mogła wystartować) | ✅ naprawiono |

---

## 1. Błędy krytyczne

### E1 — Pociski wrogów nigdy się nie poruszają (`enemy_bullet.py:16-27`)

`EnemyBullet.update(delta_time)` nadpisuje metodę bazową, **nie wywołując `super().update(delta_time)`**. W arcade 3.x to właśnie `Sprite.update()` stosuje `change_x`/`change_y` (sprawdzone empirycznie: sprite z nadpisanym `update` bez `super()` nie porusza się; zwykły sprite z `change_x` się porusza).

Skutki:
- `change_y = -BULLET_SPEED` (`game_view.py:353`) nigdy nie jest stosowany — pociski wrogów **wisia w zawieszeniu** pod strzelającym wrogiem.
- Warunek sprzątania `if bullet.top < 0: remove_from_sprite_lists()` (`game_view.py:396`) nigdy się nie spełni — pociski **kumulują się bez limitu** (wyciek pamięci + zagęszczenie ekranu).
- Gracz nigdy nie może zostać trafiony przez pocisk wroga — główny mechanizm zagrożenia w grze nie działa.

**Poprawka:** dodać `super().update(delta_time)` na początku `EnemyBullet.update` (analogicznie do `EnemyInvader.update`, gdzie nie jest potrzebne, bo wrogowie nie używają `change_x/y`).

> ✅ **NAPRAWIONO (2026-10-30):** dodano `super().update(delta_time)` jako pierwszą linię `EnemyBullet.update` (`enemy_bullet.py`). Zweryfikowano testem runtime: pocisk z `change_y = -5` po `update(1/60)` przesunął się z y=500 do y=495 — pociski spadają i są sprzątane przez warunek `bullet.top < 0`.

### E2 — `clear()` nie zatrzymuje pętli → utrata wielu żyć w jednej klatce (`game_view.py:366-397`)

W `process_enemy_bullets` po trafieniu gracza wywoływane jest `self.enemy_bullet_list.clear()` (`:388`), ale pętla `for bullet in self.enemy_bullet_list:` **kontynuuje iterację po starej liście**.

Sprawdzone empirycznie w arcade 3.3.3: `SpriteList.__iter__` zwraca `iter(self.sprite_list)`, a `SpriteList.clear()` **zamienia** `self.sprite_list` na nowy pusty list — iterator pętli `for` trzyma odwołanie do starej listy (test: po `clear()` w połowie iteracji wizytowane indeksy to `[0,1,2,3,4]`).

Skutki (w obecności E1 pociski są zamarznięte w powietrzu, więc nakładanie się na gracza jest prawdopodobne):
- każdy kolejny pocisk z starej listy nakładający się na gracza ponownie odjęwa życie (`:387`) i odtwarza dźwięk eksplozji,
- przy `lives == 0` w tej samej klatce następuje `game_state = GAME_OVER` + dźwięk game over (`:391-393`),
- `clear()` wywoływane powtórnie jest bezskuteczne dla trwającej iteracji.

**Poprawka:** po obsłużeniu trafienia gracza wyjść z pętli — dodać `break` po bloku `if arcade.check_for_collision(self.player_sprite, bullet):` (zamiast `continue`), np.:

```python
if arcade.check_for_collision(self.player_sprite, bullet):
    if self.lives > 0:
        ...
    else:
        ...
    break
```

> ✅ **NAPRAWIONO (2026-10-30):** dodano `break` po bloku trafienia gracza w `process_enemy_bullets` (`game_view.py:394-396`) — po `clear()` pętla nie sprawdza już pozostałych pocisków ze starej listy. Zweryfikowano symulacją: 3 pociski nakładające się na gracza → dokładnie 1 trafienie w klatce, lista pocisków pusta po klatce.

### E13 — `Rect(0,0,w,h)` i `Point2(...)` nie istnieją w 3.3.3 → crash konstrukcji `GameView` (`game_view.py:64,65,236,238`)

W arcade 3.3.3 `arcade.types.Rect` to **8-pole NamedTuple** (`left, right, bottom, top, width, height, x, y`), a `arcade.types.Point2` to **alias typu** (`Union[tuple, Vec2]`) — nie klasa. Zapisy `Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)` (`:64`) i `Point2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)` (`:65`) wyrzucają `TypeError: Rect.__new__() missing 4 required positional arguments` / `'typing.Union' object is not callable`.

Skutek: `GameView()` **crashował w `__init__`** — gra nie mogła przejść dalej niż "Click to Start" (`main.py` nie buduje `GameView`, dopóki gracz nie kliknie). Ta sama 4-argumentowa forma `Rect(0, 0, window_w, window_h)` w `on_draw` (`:236`) i `Point2(...)` (`:238`) crashowałyby przy pierwszej klatce.

Zauważenie: analiza **E7** zakładała, że konstrukcja kamery z `Rect(0,0,1200,1000)` działa (±600/±500). W 3.3.3 tak nie jest — kod nie działał w ogóle. Po naprawie E13 opis E7 pozostaje aktualny: projekcja ustalana w konstrukcji (±600/±500), a późniejsza zmiana `viewport`/`zoom` (`:236-237`) jej nie przelicza.

**Poprawka:** użyć wbudowanych w 3.3.3 konstruktorów pomocniczych: `arcade.types.Viewport(left, bottom, width, height)` (zwraca poprawny 8-pole `Rect`) dla viewportu, oraz `pyglet.math.Vec2` (już importowany) dla pozycji kamery (setter `Camera2D.position` akceptuje `Point`, czyli krotkę lub `Vec2`).

> ✅ **NAPRAWIONO (2026-10-30):** zamieniono `Rect(0, 0, w, h)` → `Viewport(0, 0, w, h)` (`game_view.py:64,236`) i `Point2(x, y)` → `Vec2(x, y)` (`game_view.py:65,238`); usunięto zbędne importy `Rect`/`Point2`. Zweryfikowano testem runtime (headless): `GameView()` konstruuje się bez błędu, `camera.viewport` ma poprawne 8 pól, `on_draw()` i `on_update()` działają. Ta naprawa była **wymagana do empirycznej weryfikacji E3/E4/E6** (bez niej żaden test runtime nie mógł wystartować).

---

## 2. Błędy logiczne

### E3 — Martwe (wybuchające) wrogowie są poruszane i wywołują odwrócenie (`game_view.py:304-328`)

`update_enemies` iteruje po całej `enemy_list`, **bez sprawdzania `enemy.dead`**:
- pętla ruchu (`:307-308`) przesuwa też trupy — wybuch dryfuje w poziomie (~1.5 px/klatkę ≈ 45 px w 0.5 s przy 60 fps, podczas których trupa istnieje, patrz `enemy_invader.py:19-22`),
- kontrola krawędzi (`:313-321`) może zostać wywołana przez trupa znajdującą się blisko krawędzi → **fałszywe odwrócenie kierunku i spuszczenie całej formacji o 30 px** (`:324-328`),
- pętla spuszczania w dół (`:326-328`) też przesuwa trupy.

**Poprawka:** `if enemy.dead: continue` w każdej z trzech pętli (albo filtrowanie trupów poza `enemy_list`).

> ✅ **NAPRAWIONO (2026-10-30):** dodano `if enemy.dead: continue` na początku każdej z trzech pętli w `update_enemies` (ruch, kontrola krawędzi, spuszczanie formacji — `game_view.py:307-336`). Zweryfikowano testem runtime (headless): trupa umieszczona przy lewej krawędzi (`left = -33 < LEFT_ENEMY_BORDER`) **nie jest przesuwana** i **nie wywołuje** fałszywego odwrócenia kierunku ani spuszczania formacji (kierunek i wszystkie `y` bez zmian); żywy wróg na krawędzi nadal odwraca kierunek (`change_x: -1.5 → 1.5`) i spuszcza formację o 30 px — trupa pozostaje w miejscu.

### E4 — Strzela górny, a nie dolny wróg kolumny; `chance` liczy trupy (`game_view.py:330-364`)

Komentarz (`:335-336`) deklaruje, że dzięki porządkowi listy „tylko dolny rząd może strzelać". W rzeczywistości `setup_level_one` (`:89-118`) buduje listę **kolumnowo, od `row 0` (y=720 — górny rząd)**, więc pierwszy żywy wróg danej kolumny w kolejności listy to **najwyżej leżący**, to on dostaje szansę strzału (mechanizm `x_spawn` w `:348` i `:364` blokuje pozostałych w kolumnie). Pociski wychodzą więc od czubka formacji, a nie od jej dołu — zmienia to tempo rozgrywki (gracz dostaje więcej czasu na reakcję).

Dodatkowo `chance = 3 + len(self.enemy_list)` (`:344`) liczy **trupy** (martwi wrogowie pozostają w liście przez 0.5 s).

**Poprawka:** wybór strzelca per kolumna od najniższego żywego wroga (np. dict `x -> najniższy żywy` albo iteracja w drugą stronę) oraz `chance = 3 + liczba żywych wrogów`.

> ✅ **NAPRAWIONO (2026-10-30):** w `allow_enemies_to_fire` (`game_view.py:338-376`) dodano wybór strzelca per kolumna: słownik `lowest_by_x` budowany przez iterację `reversed(self.enemy_list)` — pierwszy żywy wróg danej kolumny w odwróconej kolejności listy to najniższy żywy; jedno losowanie na kolumnę. `chance = 3 + liczba żywych wrogów` (generator `not enemy.dead`) liczony raz, przed pętlą losowań. Zweryfikowano testem runtime (headless, `random.randrange` stubowane na 0, żeby każda kolumna strzelała):
> - pełna formacja (50 żywych, 10 kolumn) → dokładnie 10 pocisków, **wszystkie z dolnego rzędu** (środek y=888; nie z górnego rzędu y=648), `chance = 3 + 50 = 53`;
> - po zabiciu całego górnego rzędu (10 trupów w liście) i dolnego wroga kolumny 5 → kolumna 5 strzela z nowego najniższego żywego (y=828), pozostałe 9 kolumn z y=888, `chance = 3 + 39 = 42` (trupy nie liczą się do szansy);
> - przy 6 żywych wrogach w 2 kolumnach → dokładnie 2 losowania, `chance = 3 + 6 = 9` (kolumny bez żywych nie losują).

### E5 — Jeden pocisk gracza zabija kilku wrogów (`game_view.py:399-433`)

`for enemy in hit_list:` (`:420`) nie wychodzi z pętli po pierwszej kolizji: pocisk jest usuwany po zabiciu pierwszego wroga (`:423`), ale pętla **kontynuuje** i zabija każdego kolejnego wroga, z którym pocisk się nakłada — podwójny/trzykrotny zapis wyniku (`:426`) i dźwięków. Drugie wywołanie `remove_from_sprite_lists()` jest bezszkodne (idempotentne) lecz redundantne. W oryginale pocisk znika po pierwszym trafieniu.

**Poprawka:** `break` po pierwszej nie-ofiarnej (nie `dead`) kolizji.

> ✅ **NAPRAWIONO (2026-10-30):** dodano `break` po pierwszej żywej (nie `dead`) kolizji w pętli `for enemy in hit_list:` (`game_view.py:437-449`) — pocisk zabija tylko pierwszego żywego wroga, a pozostałe trafienia z `hit_list` nie są już liczone; drugi wywołany `remove_from_sprite_lists()` zniknął (został jeden). Zweryfikowano testem runtime (headless, bez okna — `GameView` przez `__new__`, stub `arcade.play_sound`):
> - 3 nakładające się wrogowie + 1 pocisk → dokładnie **1 zabójstwo**, wynik +30 (tylko pierwszy wróg z `hit_list`), 1 odtworzenie dźwięku trafienia, pocisk usunięty z listy;
> - pocisk nakładający się na 2 trupy + żywy wróg za nimi → trupy pomijane, pocisk zabija pierwszego żywego i jest konsumowany, wynik tylko za żywego;
> - pocisk nakładający się wyłącznie na trupy → nie jest konsumowany (przelatuje dalej, wynik 0).
> Test wykrywalności: ten sam scenariusz 1 na kodzie przed naprawą (HEAD) dawał 3 zabójstwa — test zawodził, po naprawie przechodzi.

### E6 — Pociski wrogów aktualizowane dwukrotnie w klatce (`game_view.py:444` i `:369`)

`on_update` wywołuje `self.enemy_bullet_list.update(delta_time)` (`:444`), a następnie `process_enemy_bullets` wywołuje `self.enemy_bullet_list.update()` (`:369`). Obecnie (przez E1) podwaja tylko animację pocisku (~2× szybszy cykl tekstur); **po naprawie E1 podwoiłaby też prędkość** pocisków wrogów.

**Poprawka:** usunąć jedno z wywołań (zostać z jednym `update` na klatkę).

> ✅ **NAPRAWIONO (2026-10-30):** usunięto `self.enemy_bullet_list.update(delta_time)` z `on_update` (`game_view.py:444`) — pozostał pojedynczy `update` w `process_enemy_bullets` (`:369`). Pociski wrogów spadają z prędkością `BULLET_SPEED` (nie 2×). Efekt uboczny: w stanie GAME_OVER pociski zamarzają wraz z resztą pola (zamiast lecieć poza ekran i kumulować się bez sprzątania).

---

## 3. Zgodność z arcade 3.x

### E7 — Kamera distorsuje obraz po zmianie rozmiaru okna (brak letterboxa) (`game_view.py:223-238`)

W arcade 3.3.3 projekcja `Camera2D` jest **ustalana w chwili konstrukcji** (tu: `Rect(0,0,1200,1000)` → ±600/±500; `camera_2d.py`, `__init__`). Późniejsza zmiana `zoom` (`:237`) i `viewport` (`:236`) nie przelicza projekcji — widoczny obszar świata to `1200/zoom × 1000/zoom` mapowany na rozmiar okna, czyli **skalowanie niejednostajne**, gdy stos okna ≠ 1200:1000.

Przykład: okno 1600×900 → `zoom = min(1600/1200, 900/1000) = 0.9` → 1.2 px/jednostkę w osi X, a 0.81 px/jednostkę w osi Y (~48% rozciągnięcia w poziomie). Komentarz `:233-234` („czarne pasy pojawią się, gdy stosy różnią się") jest **błędny** — pasów nie ma wcale; jest za to zniekształcenie. Okno jest `resizable=True` (`main.py:9`), więc scenariusz występuje w praktycie.

**Poprawka:** wbudowana w 3.3.3 metoda `self.camera.match_window(aspect=SCREEN_WIDTH / SCREEN_HEIGHT)` (ustawia viewport + projekcję + scissor z zachowaniem stosu — daje prawdziwy letterbox), ewentualnie jawny parametr `projection` przy konstrukcji kamery.

> ✅ **NAPRAWIONO (2026-10-30):** w `on_draw` (`game_view.py:233-245`) używana jest wbudowana metoda `self.camera.match_window(aspect=SCREEN_WIDTH / SCREEN_HEIGHT)` — przelicza projekcję z zachowaniem stosu 1200:1000 (prawdziwy letterbox, nie skalowanie niejednostajne). `match_window` zakotwicza letterbox w rogu okna (0, 0), więc viewport jest następnie wycentrowany: `Viewport((window_w - vp.width)/2, (window_h - vp.height)/2, vp.width, vp.height)`; linia `zoom = min(window_w/SCREEN_WIDTH, window_h/SCREEN_HEIGHT)` utrzymuje widoczny świat dokładnie na `0..1200 × 0..1000`. Konstrukcja kamery została **bez** jawnego `projection` (domyślna projekcja wycentrowana w (0,0), `position=Vec2(600,500)`) — jawna projekcja wycentrowana w (600,500) dałaby błędne pole widzenia, bo `match_window` trzyma środek projekcji stały (sprawdzone w `camera_2d.py:411-457`).

> Zweryfikowano testem runtime (headless, `Camera2D` skonfigurowana 1:1 jak w `GameView.__init__`, rzeczywiste `on_draw`):
> - 1200×1000 (natywny): viewport (0,0,1200,1000), zoom 1 — zachowanie identyczne jak przed naprawą (ścieżka filtra CRT nietknięta);
> - 1600×900: paski po lewej i prawej po 260 px, jednolita skala 0.9 px/jednostkę w obu osiach — przed naprawą było 1.200 vs 0.810 px/jednostkę (~48% zniekształcenia); `unproject` czterech rogów viewportu → dokładnie (0,0), (1200,0), (0,1000), (1200,1000);
> - 1920×1080: paski boczne 312 px, skala 1.08; 800×1000: paski górny/dolny ~167 px, skala 0.667; 600×1000: skala 0.5; 2000×800: paski boczne 520 px, skala 0.8 — we wszystkich rozmiarach skala jednolita (test wykrywalności: na kodzie przed naprawą przy 1600×900 osie X i Y miały różne skale — test zawodził, po naprawie przechodzi).

### E8 — Surowe współrzędne myszy traktowane jako współrzędne świata (`game_view.py:260-271`)

Zdarzenia myszy dostarczają **surowe piksele ekranu** (widok zarejestrowany jako handler pygleta; transformacja kamery nie jest aplikowana automatycznie), a kod nadaje je bezpośrednio: `self.player_sprite.center_x = x` (`:267`) oraz clamp `min(max(x, margin), SCREEN_WIDTH - margin)` (`:271`). Przy `zoom ≠ 1` (każde okno inne niż 1200×1000) kursor i statek **rozjeżdżają się** — zarówno pozycja, jak i „prędkość" ruchu gracza względem kursora są błędne.

Dodatkowo `:267` jest **martwą linią** — wartość jest natychmiast nadpisana w `:271` (patrz też E10).

**Poprawka:** przeliczenie ekran → świat przez `self.camera.unproject((x, y))` (dostępne w 3.3.3, `camera_2d.py:305`) i użycie `world.x` w clampie.

> ✅ **NAPRAWIONO (2026-10-30):** `on_mouse_motion` (`game_view.py:267-283`) przelicza surowe piksele ekranu na współrzędne świata przez `self.camera.unproject((x, y))` i clampuje `world.x`: `min(max(world.x, margin), SCREEN_WIDTH - margin)`. Martwa linia `:267` zniknęła (patrz **E10**). Pierwotnie marginesem był `ENEMY_HORIZONTAL_MARGIN`; osobny margines gracza (połowa szerokości sprite'a) to punkt **E12** (naprawiony 2026-10-30).

> Zweryfikowano testem runtime (headless, rzeczywiste `on_mouse_motion`):
> - 1200×1000: kursor w (600, 500) → statek x=600 — zachowanie identyczne jak przed naprawą;
> - 1600×900: kursor w środku okna → statek x=600; przesunięcie kursora o +100 px → statek +111.1 jednostki świata (100 px / 0.9 px/jednostkę) — kursor i statek nie rozjeżdżają się (przed naprawą statek poruszałby się 1:1 w pikselach);
> - kursor w czarnym pasie letterboxa → `unproject` daje x < 0 / x > 1200 → statek clampowany do 48 / 1152 (po naprawie **E12**: margines = połowa szerokości sprite'a; przed E12 było 15 / 1185) — statek nie wychodzi poza pole gry.

### E9 — Czcionka „Kenney Rocket" nigdy nie jest wczytywana (`game_view.py:189,199,210,219`)

`font_name="Kenney Rocket"` w `arcade.draw_text` — czcionka nie jest zainstalowana systemowo (sprawdzone `fc-list`: brak), a gra **nigdy nie rejestruje jej u pygleta** (arcade 3.3.3 pakuje ją pod `:system:fonts/ttf/Kenney/Kenney_Rocket.ttf`, ale nie oferuje żadnej funkcji typu `load_kenney_fonts`). Łańcuch `draw_text` → `_attempt_font_name_resolution` (`arcade/text.py:105`) → `resolve()` (nie odnajduje samej nazwy) → `pyglet.font.load(("Kenney Rocket",))` — a `load` przy braku pasującego fontu **cicho zwraca domyślną czcionkę systemową** (dokumentacja: „If no font can be matched to the name(s), a default font is used"). Brak crashu, ale wygląd HUD/Game Over jest inny niż zamierzony.

**Poprawka:** zarejestrowanie wbudowanej czcionki przy starcie — `arcade.load_font(":system:fonts/ttf/Kenney/Kenney_Rocket.ttf")` (w `main.py`) — albo usunięcie parametru `font_name`.

> ✅ **NAPRAWIONO (2026-10-30):** w `main()` przed utworzeniem okna dodano `arcade.load_font(":system:fonts/ttf/Kenney/Kenney_Rocket.ttf")` (`main.py`). Uwaga: pierwotnie proponowane `arcade.load_kenney_fonts()` **nie istnieje w 3.3.3** (sprawdzone: `AttributeError`); `arcade.load_font` robi dokładnie to, co by robiła — `resolve(path)` + `pyglet.font.add_file(...)` (`arcade/text.py:98-99`). Plik ma poprawną tabelę nazw (rodzina `Kenney Rocket`, waga `Regular` — rozstrzyganie nazw jest case-insensitive).
>
> Zweryfikowano testem runtime (headless, `pyglet.options['headless'] = True`):
> - przed rejestracją: `have_font("Kenney Rocket") = False`, `_attempt_font_name_resolution("Kenney Rocket")` → `'Noto Sans'` — cicha substytucja domyślną czcionką systemową (test wykrywalności: ten sam scenariusz na kodzie przed naprawą);
> - po `arcade.load_font(...)`: `have_font("Kenney Rocket") = True`, `_attempt_font_name_resolution("Kenney Rocket")` → `'Kenney Rocket'`;
> - na poziomie pygleta: `pyglet.font.load(("Kenney Rocket",))` → `FreeTypeFont` o `name == 'Kenney Rocket'`.
> Rejestracja jest klasowa (`FreeTypeFont._memory_faces`, nie per-kontekst GL), więc wywołanie przed `arcade.Window(...)` jest bezpieczne; w grze rejestracja następuje przed jakimkolwiek wywołaniem `draw_text`.

---

## 4. Drobiazgi

### E10 — Martwa linia w `on_mouse_motion` (`game_view.py:267`)

`self.player_sprite.center_x = x;` jest od razu nadpisane w `:271` (`min(max(x, margin), ...)`). Usunąć linię `:267` (wraz z przejściem na `unproject` z E8).

> ✅ **NAPRAWIONO (2026-10-30):** linia została usunięta jako efekt uboczny przejścia na `unproject` (punkt **E8**) — `on_mouse_motion` nadaje `center_x` teraz tylko raz, już w przeliczonych współrzędnych świata (`game_view.py:280`).

### E11 — Dowolny przycisk myszy działa (`game_view.py:285-297`, `instruction_view.py:20-26`)

`on_mouse_press` ignoruje parametr `button`: prawy i środkowy przycisk strzelają pocisk, a w `InstructionView` — startują grę. Warto sprawdzić `button == arcade.MOUSE_BUTTON_LEFT`.

**Poprawka:** na początku `on_mouse_press` (obie klasy) dodać wczesny `return`, gdy `button != arcade.MOUSE_BUTTON_LEFT`.

> ✅ **NAPRAWIONO (2026-10-30):** w `GameView.on_mouse_press` (`game_view.py:288-290`) oraz `InstructionView.on_mouse_press` (`instruction_view.py:22-24`) dodano odrzucenie nie-lewych przycisków:
> ```python
> if button != arcade.MOUSE_BUTTON_LEFT:
>     return
> ```
> Stałe w arcade 3.3.3 sprawdzone empirycznie: `arcade.MOUSE_BUTTON_LEFT == 1`, `MOUSE_BUTTON_MIDDLE == 2`, `MOUSE_BUTTON_RIGHT == 4` (są eksportowane z `arcade`, nazwy zgodne z 3.x).
>
> Zweryfikowano testem runtime (bez okna — `GameView` przez `__new__`, stub `camera`, `play_sound` i `window.show_view`):
> - `GameView`: prawy i środkowy przycisk → 0 pocisków, 0 dźwięków; lewy → dokładnie 1 pocisk i 1 dźwięk wystrzału;
> - `InstructionView`: prawy i środkowy przycisk → brak `show_view`; lewy → dokładnie jedno przejście do `GameView`.

### E12 — Gracz wychodzi poza krawędź ekranu (`game_view.py:278-283`)

Clamp używa `ENEMY_HORIZONTAL_MARGIN = 15` dla stateka o szerokości 96 px (16 px × 6) — środek może stanąć na 15 px od krawędzi, więc połowa stateka (~33 px) wyjdzie poza ekran. Warto osobną stałą dla gracza, np. `HALF_PLAYER_WIDTH + margin`.

**Poprawka:** clampować do połowy szerokości sprite'a gracza: `margin = self.player_sprite.width / 2` (48 px), niezależnie od marginesu wrogów.

> ✅ **NAPRAWIONO (2026-10-30):** w `on_mouse_motion` (`game_view.py:278-283`) margines clampu to połowa faktycznej szerokości sprite'a: `margin = self.player_sprite.width / 2` (= 96/2 = 48 px), a nie `ENEMY_HORIZONTAL_MARGIN` (15 px). Wartość jest brana z `Sprite.width` (tekstura 16×16 × skala 6), więc automatycznie nadąża za zmianą `SPRITE_SCALING_PLAYER` — stała w `constants.py` nie zdesynchronizuje się. `ENEMY_HORIZONTAL_MARGIN`/`LEFT_ENEMY_BORDER`/`RIGHT_ENEMY_BORDER` pozostają nietknięte (nadal 15 px dla formacji wrogów).
>
> Zweryfikowano testem runtime (bez okna — stub `camera.unproject` = identyczność, czyli natywne 1200×1000):
> - kursor na `x = 0` → środek statku 48, **lewa krawędź obrazu = 0** (przed naprawą: −33 px poza ekran);
> - kursor na `x = -500` (poza ekranem / w czarnym pasie letterboxa) → nadal środek 48, statek w całości na ekranie;
> - kursor na `x = 1200` i `x = 1700` → środek 1152, **prawa krawędź = 1200** (przed naprawą: 1233);
> - kursor w środku (`x = 600`) → środek statku 600 — śledzenie kursora 1:1 bez zmian;
> - stałe marginesu wrogów bez zmian (`ENEMY_HORIZONTAL_MARGIN = 15`).
>
> Uwaga: `Sprite.left`/`Sprite.right` w arcade 3.3.3 liczą się z **przyciętego hit boxa** (bbox nieprzezroczystych pikseli `player.png`: 13×8 px → 78×48 po skalowaniu), a nie z pełnego quada tekstury — dlatego test sprawdza faktyczne krawędzie rysowania (`center_x ± width/2`), nie `sprite.left/right`.

---

## 5. Zweryfikowane — bez błędów

Sprawdzone w kontekście arcade 3.3.3 i **nie wymagają zmian**:

- **Ścieżki dźwięków** `":resources:sounds/hurt5.wav"`, `hit5.wav`, `explosion1.wav`, `gameover4.wav` (`game_view.py:70-73`) — sprawdzono empirycznie: `arcade.load_sound(":resources:sounds/hurt5.wav")` **rozstrzyga się poprawnie** (handle `:resources:` → `arcade/resources/{system,assets}`, pliki leżą w `assets/sounds/`). Brak crashu przy „Click to Start". (Zauważenie: wariant `:resources:assets/sounds/...` się **nie** rozstrzyga — obecna forma w kodzie jest właściwa.)
- **CRT filter** (`game_view.py:46-57`, `:240-252`) — sygnatura konstruktorów `arcade.experimental.CRTFilter(width, height, resolution_down_scale, hard_scan, hard_pix, display_warp, mask_dark, mask_light)` oraz `use()`/`clear()`/`draw(time=0, target=None)` (wołane bez argumentów — poprawnie) są zgodne z 3.3.3; wyłączenie filtra po resize (`:229-231`) jest rozsądne.
- **API `SpriteList`** — `append`, `clear`, `update` istnieją i są użyte poprawnie; usuwanie elementu podczas iteracji `for` **nie pomija** kolejnych elementów (sprawdzone).
- **`View.window`** — ustawiane w `View.__init__` przez `arcade.get_window()` (`application.py:1309`, `Window.__init__` wywołuje `set_window(self)`), więc dostęp do `self.window` w `GameView.__init__` (`game_view.py:59`) jest bezpieczny. (Uwaga 2026-10-30: sam `GameView.__init__` crashował przy konstrukcji kamery — 4-arg `Rect`/`Point2` — patrz **E13**, naprawiono.)
- **`requirements.txt`** — `arcade>=3,<4`, zgodne z zainstalowaną 3.3.3.
- **Rozmiary tekstur** — wrogowie/gracz 16×16, pocisk wroga 8×8, pocisk gracza 4×4 (skalowanie ×6) — spójne z geometrią kolizji.

---

## Rekomendacja kolejności napraw

Wykonane (2026-10-30):

1. ✅ **E1** (`super().update` w `EnemyBullet`) — fundament rozgrywki.
2. ✅ **E2** (`break` po trafieniu gracza) — wraz z E1 pociski spadają; bez `break` każda klatka nakładania się = -1 życie.
3. ✅ **E6** — usunięto podwójne `update` (bez tego po E1 pociski leciałyby 2× za szybko).
4. ✅ **E3** — trupy nie są poruszane i nie wywołują odwrócenia formacji.
5. ✅ **E4** — strzela najniższy żywy wróg kolumny; `chance` liczy tylko żywych.
6. ✅ **E13** — `Viewport`/`Vec2` zamiast 4-argumentowych `Rect`/`Point2`; odblokowało empiryczną weryfikację (E3/E4/E6 nie dało się przetestować, póki `GameView()` nie można było skonstruować).
7. ✅ **E5** (`break` po pierwszej żywej kolizji) — jeden pocisk zabija tylko jednego wroga; wynik i dźwięk nie dublują się.
8. ✅ **E7** (`match_window(aspect=...)` + wycentrowany viewport + `zoom` w `on_draw`) — prawdziwy letterbox, jednolita skala, brak zniekształceń przy resize okna.
9. ✅ **E8** (`unproject((x, y))` w `on_mouse_motion`) — surowe piksele myszy przeliczane na współrzędne świata; kursor i statek nie rozjeżdżają się.
10. ✅ **E10** — martwa linia `:267` usunięta jako efekt uboczny przejścia na `unproject` (E8).
11. ✅ **E9** — `arcade.load_font(":system:fonts/ttf/Kenney/Kenney_Rocket.ttf")` w `main.py` (przed `arcade.Window`) — wbudowana czcionka zarejestrowana; `font_name="Kenney Rocket"` w HUD/Game Over rozstrzyga się poprawnie zamiast cicho substytuować domyślną czcionkę. (Pierwotnie proponowane `arcade.load_kenney_fonts()` nie istnieje w 3.3.3.)
12. ✅ **E11** — `if button != arcade.MOUSE_BUTTON_LEFT: return` w `GameView.on_mouse_press` i `InstructionView.on_mouse_press` — prawy/środkowy przycisk nie strzela i nie startuje gry.
13. ✅ **E12** — clamp gracza do `self.player_sprite.width / 2` (48 px) zamiast `ENEMY_HORIZONTAL_MARGIN` (15 px) — statek pozostaje w całości na ekranie; margines wrogów bez zmian.

Zostaje do zrobienia:

- _(brak — wszystkie pozycje z listy E1–E13 są naprawione)_
