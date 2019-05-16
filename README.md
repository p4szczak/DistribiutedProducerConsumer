
  

# DistribiutedProducerConsumer


**Wykorzystane narzędzia** 

Projekt został zrealizowany przy pomocy języka Python3 i biblioteki mpi4py.
  
Do realizacji wzajemnego wykluczania został wykorzystany algorytm Suzuki-Kasami oparty na tokenach.


**Struktura plików**
  
| Pik | Opis |
| ------ | ------ |
| main.py | główny plik projektu przypisujący role poszczególnym procesom i wywołujący metody w zależności od roli przypisanej procesowi |
| Monitor.py | plik zawiera klasę realizującą implementację rozproszonego monitora w oparciu o algorytm Suzuki-Kasami, dodatkowo strukturę stworzoną dla zapytań oraz enum z tagami wiadomości |
| Token.py | plik reprezentuje klasę - Token, czyli strukturę danych przesyłaną pomiędzy procesami |
| Client.py | klasa konsumenta, dziedziczy po klasie Monitor |
| Producer.py | klasa producenta, dziedziczy po klasie Monitor |

**Opis klasy Token**

* tablica LN &rarr; numer ostatniego zapytania, kiedy token został poprawnie przydzielony dla procesu j-etgo

* queue &rarr; kolejka główna przechowująca procesy oczekujące na token

* condQueue &rarr; słownik posiadający kolejki warunkowe

* inStock &rarr; liczba elementów znajduących się w magazynie (rozszerzenie wykorzystane dla rozwiązania problemu Producenta i Konsumenta)

**Opis metod klasy Monitor**


* `enterCS()` &rarr; w momencie, gdy proces i-ty próbuje wejść do sekcji krytcznej, sprawdza czy nie posiada tokenu. Jeżeli proces i-ty posiada token oznacza to, że proces i-ty jest uprawniony do wejścia do sekcji krytycznej. W przeciwnym wypadku wysyła zapytanie o token do wszystkich procesów i czeka na jego otrzymanie. W momencie otrzymania tokenu proces staje się uprawniony by wejść do sekcji krytycznej.

* `exitCS()` &rarr; w momencie, gdy proces opuszcza sekcję krytyczną sprawdza, czy wystąpiły zapytania o token, jeżeli tak przesyła token do następnego procesu z kolejki.

* `wait(zmienna_warunkowa)` &rarr; proces i-ty dodaje swoje ID do odpowiedniej kolejki warunkowej w i zwalnia token, po czym oczekuje na ponowne otrzymanie tokenu upoważniającego go do wejścia do sekcji krytycznej

* `signal(zmiana_warunkowa)` &rarr; proces i-ty wykonując metodę signal na zmiennej warunkowej, przenosi jeden z procesów z kolejki warunkowej do głównej kolejki procesów oczekujących na token

* `signalAll(zmiana_warunkowa)` &rarr; proces i-ty wykonując metodę signalAll na zmiennej warunkowej, przenosi wszystkie procesy z kolejki warunkowej do głównej kolejki procesów oczekujących na token.

* `kill()` &rarr; proces i-ty wysyła do wszystkich innych procesów wiadomość o swojej śmierci i zmienia wartość zmiennej `threadLive` na `false`

* `recieverThread()` &rarr; wątek poboczny odbierający wiadomości od innych procesów:
&rarr; w przypadku, gdy proces i odbierze zapytanie o token od procesu j-tego sprawdza, czy wiadmość jest przestarzała, jeżeli nie aktualizuje lokalną tablicę z numerami zapytań. Następnie, jeżeli proces i-ty posiada token i nie jest w sekcji krytycznej, przesyła go procesowi j-temu.
&rarr; jeżeli proces i-ty odbierze wiadomość o śmierci procesu j-tego - zwiększa liczbę procesów nieżywych. Wątek kończy pracę w momencie gdy: zmienna `threadLive` jest równa `false` i proces nie posiada tokenu lub gdy proces i-ty pozostał ostatnim procesem żyjącym.

**Dodatkowe wymagania przed uruchomieniem**

* apt-get install libcr-dev mpich mpich-doc
* pip install mpi4py

**Uruchomienie programu**

`mpiexec -n {liczba_procesów} python3 main.py`
