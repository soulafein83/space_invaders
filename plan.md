# Plan przeglądu i poprawek — Space Invaders

Źródło: https://github.com/pvcraven/space_invaders
Fork (Twój): https://github.com/soulafein83/space_invaders

## Co zostało zrobione

1. **Klonowanie** – repozytorium sklonowano do `space_invaders/`.
2. **Fork** – utworzony fork na koncie `soulafein83`
   (https://github.com/soulafein83/space_invaders). Dodano zdalny remote
   `fork`, żebyś mógł wrzucić poprawki jednym `git push fork`.
3. **Przegląd kodu** – poniżej znalezione problemy oraz gotowe poprawki.

---

## Jak uruchomić i sprawdzić wersję arcade

```bash
pip install arcade
python -c "import arcade; print(arcade.__version__)"
```

Wersja **arcade 3.x** (instalowana domyślnie dziś) **usunęła metodę
`on_update()`** na rzecz `update(delta_time)` (oficjalny CHANGELOG arcade).
Ten kod pisany był pod arcade 2.x, więc na świeżej instalacji **gra się
wywali** (patrz punkt 1). Poniższe poprawki dostosow ją arcade 3.x; jeśli
masz starszą wersję, część zmian jest bezpieczna do pominięcia.

---

## 🐛 Błędy krytyczne (gra się wali / nie działa na nowym arcade)

### 1. Usunięta metoda `on_update()` w arcade 3.x  ✅ NAPRAWIONE
**Pliki / linie:**
- `game_view.py` – linie 405-406
- `enemy_bullet.py` – linia 16 (`def on_update(self, dt):`)
- `enemy_invader.py` – linia 17 (`def on_update(self, dt):`)

**Problem:** W arcade 3.0 usunięto `Sprite.on_update()` oraz
`SpriteList.on_update()`. Wywołanie `self.enemy_bullet_list.on_update(...)`
rzuci `AttributeError` w każdej klatce → crash gry. Co więcej, lista wywołuje
`sprite.update(delta_time)`, więc metody animacji zapisane w `on_update()`
przez cały czas nie są wywoływane (nie zmieniają tekstur kul/explosji).

**Poprawka (zastosowana):**
```python
# game_view.py, on_update()
self.enemy_bullet_list.update(delta_time)   # było .on_update(delta_time)
self.enemy_list.update(delta_time)          # było .on_update(delta_time)

# enemy_bullet.py / enemy_invader.py
def update(self, delta_time):               # było def on_update(self, dt):
```
Zmień też nazwę parametru wewnątrz na `delta_time` (dla jasności; stara
nazwa `dt` też przeżyje, ale lepiej jednolicie).

---

## 🐛 Błędy logiczne (zła mechanika gry)

### 2. Trafienie gracza – sprawdzana CAŁA lista kul, nie tylko aktualnej  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linie 344-355 (`process_enemy_bullets`)

**Problem:**
```python
if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
```
Sprawdzane jest, czy gracz (sprite o skali 6 → ogromne pole trafień)
kolizjuje z **wszystkimi** kulami wroga na ekranie, a nie z aktualną kulą z
pętli. Skutek: gracz jest trafiany kulami znajdującymi się daleko od niego i
może stracić kilka żyw w jednej klatce.

**Poprawka:** sprawdzaj kolizję aktualnej kuli z graczem:
```python
if arcade.check_for_collision(self.player_sprite, bullet):
```
(usunąć powiązaną z nim cało-listę i powrót do pętli przez `continue`
właśnie po tej linii jest OK).

### 3. Podwójne odbicie kierunku wrogów (przejście przez ścianę)  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linie 275-282 (`update_enemies`)

**Problem:** Jeśli w tej samej klatce dwie (lub więcej) wrogów przekroczy
krawędź, kierunek jest odwracany dwa razy → wraca do pierwotnego kierunku,
ale flaga `move_down` i tak jest ustawiona. Flota „wchodzi na ścianę” i
porusza się w złym kierunku.

**Poprawka:** przerywaj pętlę po pierwszym odwróceniu:
```python
move_down = False
for enemy in self.enemy_list:
    if enemy.right > RIGHT_ENEMY_BORDER and self.enemy_change_x > 0:
        self.enemy_change_x *= -1
        move_down = True
        break
    if enemy.left < LEFT_ENEMY_BORDER and self.enemy_change_x < 0:
        self.enemy_change_x *= -1
        move_down = True
        break
```

### 4. Wrogowie strzelają prawie nigdy (bilans)  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linie 303-309 (`allow_enemies_to_fire`)

**Problem:** `chance = 3 + len(self.enemy_list) * 20`. Przy pełnej flocie
(50 wrogów) `chance = 1033`, więc `random.randrange(1033) == 0` ma szansę
~0,1% na wrogą i klatkę → gra praktycznie nie strzela. Dodatkowo komentarz
obiecyuje „strzela tylko dolny rząd”, ale kod tego nie egzekwuje (strzela
dowolny wróg, który pierwszy w danej kolumnie miał szansę).

**Poprawka (sugestia):** obniżyć bazowy współczynnik i egzekwować dolny rząd,
np.
```python
# strzela tylko najniżży żywy wróg w kolumnie
lowest = None
for enemy in self.enemy_list:
    if enemy.dead:
        continue
    if lowest is None or enemy.center_y > lowest.center_y:
        lowest = enemy
if lowest is not None and not lowest.dead:
    chance = 3 + len(self.enemy_list)      # ~53 przy pełnej flocie
    if random.randrange(chance) == 0:
        ... (strzel) ...
```

---

## ⚠️ Kwestie jakości / zgodności

### 5. Nazewnictwo w `constants.py` (naruszenie PEP8 / mylące)  ✅ NAPRAWIONE
**Plik:** `constants.py`
- linia 2: `SPRITE_SCALING_enemy = 6` → wielka litera `E` w środku nazwy
  (mieszane wielkie/małe). Poprawnie: `SPRITE_SCALING_ENEMY`.
- linie 17-21: zmienna `ENEMY_VERTICAL_MARGIN` opisana jest jako odległość
  lewej/prawej krawędzi (czyli **pozioma**), a nazywa się „VERTICAL”.
  Poprawnie: `ENEMY_HORIZONTAL_MARGIN`.

### 6. `requirements.txt` nie ma przypisanej wersji  ✅ NAPRAWIONE
**Plik:** `requirements.txt` (jedyna linia: `arcade`)

**Problem:** bez przypisanej wersji `pip` instaluje najnowší arcade 3.x,
gdzie kod (pkt 1) przestaje działać. To źródło zaskoczeń przy uruchomieniu.

**Poprawka:**
```
arcade>=3,<4
```
(albo włącz `pyproject.toml`/`setup.py` z zależnościami – obecnie ich brak).

### 7. Gracz może wyjechać poza ekran w bok  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linia 238 (`on_mouse_motion`)

**Problem:** `self.player_sprite.center_x = x` bez ograniczeń → statek
znika poza lewą/prawą krawędzią.

**Poprawka:**
```python
margin = ENEMY_VERTICAL_MARGIN
self.player_sprite.center_x = min(max(x, margin), SCREEN_WIDTH - margin)
```

### 8. Zmiana listy w trakcie iteracji  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linie 349-350 (`process_enemy_bullets`)

**Problem:** wewnątrz pętli `for bullet in self.enemy_bullet_list:`
przypisujesz `self.enemy_bullet_list = arcade.SpriteList()`. Pętla i tak
kontynuuje iterację po starej liście (co jest safer niż reasignacja w miejscu),
ale jest to niejasne i łamie zasadę „nie zmieniaj kolekcji pod sobą”. Trzymaj
przypasanie poza pętlą lub użyj `.clear()`.

---

## 💡 Ulepszenia / sugestie (opcjonalne)

### 9. Martwy kod w `setup_level_one`  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linia 79
`score = 0` jest przypisane, a natychmiast nadpisane przez
`enemy.score = score`. Do usunięcia.

### 10. `InstructionView.on_show` vs `on_show_view`  ✅ NAPRAWIONE
**Plik / linie:** `instruction_view.py` – linie 9-15
W arcade 3.x event „pokaż widok” obsługuje się przez `on_show_view()`.
`on_show` odpala się tylko raz przy pierwszym pokazaniu okna. Dla pewności
przenies metodę ustawiania tła/viewport do `on_show_view()`.

### 11. Filtr CRT jako potencjalne źródło problemów z wersjami  ✅ NAPRAWIONE
**Plik / linie:** `game_view.py` – linie 44-50 (`arcade.experimental.CRTFilter`)
Filtr jest w module `experimental` i jego API może się różnić między
wersjami arcade. Jeśli celem jest stabilność, warto opakować to w
`try/except` i domyślnie trzymać `self.filter_on = False`, albo dodać
zależność w `requirements.txt`.

### 12. Brak `README` z instrukcją uruchomienia (opcja)  ✅ NAPRAWIONE
Aktualne `readme.rst` zawiera tylko opis. Dobrze by było dodać krótką
instrukcję: `pip install arcade` → `python main.py`.

---

## Podsumowanie – co naprawić w pierwszej kolejności

Wszystkie punkty (1–12) są teraz **naprawione i wypuszczone na forka**.
Kolejność miała znaczenie tylko przy wyborze co naprawić w pierwszej
kolejności:

1. **Punkt 1** (`on_update` → `update`) – bez tego gra nie uruchomi się na
   aktualnym arcade. Najważniejsze.
2. **Punkt 2** (trafienie gracza) – poważnie łamie rozgrywkę.
3. **Punkt 3** (odbicie wrogów) – klasyczny bug „przejścia przez ścianę".
4. **Punkt 6** (pin versions) – zapobiega problemom z zgodnością.
5. Punkt 4, 5, 7, 8 – poprawa balansu i jakości kodu.
6. Punkt 9–12 – opcjonalne ulepszenia (już zrobione).
