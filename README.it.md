# FusionLocks

![Logo FusionLocks](logo.svg)

FusionLocks e un piccolo linguaggio di programmazione per principianti. I
programmi usano l'estensione `.fss`. Questa versione include un interprete
funzionante in Python, un avvio portabile per Windows, esempi e colori per
VS Code. Non servono pacchetti Python di terze parti.

## Scaricare e preparare la versione portabile (Windows)

1. Scarica questo repository da GitHub con **Code > Download ZIP** ed estrailo
   in una cartella, per esempio
   `C:\Users\IlTuoNome\Downloads\FusionLocks`.
2. Non serve un programma di installazione. Puoi usare Python 3 gia presente
   sul computer.
3. Per rendere autonoma la cartella, scarica il **Windows embeddable package**
   di Python 3.10 o successivo da
   [python.org/downloads/windows](https://www.python.org/downloads/windows/).
   Estrai il contenuto nella cartella `runtime` del progetto, in modo che
   esista `FusionLocks\runtime\python.exe`. L'avviatore controlla prima questo
   percorso. Quando sposti il progetto, sposta anche `runtime`.
4. In alternativa, installa Python 3 dalla stessa pagina ufficiale e seleziona
   **Add python.exe to PATH** durante l'installazione.
5. Apri il Prompt dei comandi nella cartella del progetto ed esegui:

   ```bat
   run-fusionlocks.bat examples\esempio.fss
   ```

   Oppure usa Python direttamente:

   ```bat
   python fusionlocks.py examples\esempio.fss
   ```

La cartella `runtime` non e inclusa nel repository: l'ambiente Python ha una
propria licenza. Prima di ridistribuirlo, leggi le note e le condizioni
allegate al download ufficiale di Python.

## Il tuo primo programma

Crea `ciao.fss`:

```fss
let nome = "Ada"
print "Ciao, " + nome + "!"

let n = 3
while n > 0 {
    print n
    set n = n - 1
}

if n == 0 {
    print "Fatto!"
}
```

Eseguilo:

```bat
run-fusionlocks.bat ciao.fss
```

Controlla la sintassi senza eseguire il programma:

```bat
run-fusionlocks.bat --check ciao.fss
```

## Riferimento del linguaggio

- `let nome = espressione` dichiara una variabile una sola volta.
- `set nome = espressione` cambia una variabile gia dichiarata.
- `print espressione` mostra un valore nella console.
- `if condizione { ... } else { ... }` sceglie un blocco.
- `while condizione { ... }` ripete il blocco finche la condizione booleana e
  `true`.
- Valori: numeri interi, decimali, stringhe tra virgolette, `true`, `false`.
- Operatori: `+ - * / %`, confronti `== != < <= > >=`, logica `and or not` e
  parentesi.
- `#` introduce un commento. Separa le istruzioni con una nuova riga o `;`.
- Le condizioni devono restituire `true` o `false`. I numeri non vengono
  convertiti automaticamente in testo; concatena stringhe con `+`.
- Per sicurezza, l'esecuzione si ferma dopo 100.000 istruzioni.

## VS Code

La cartella `vscode-extension` contiene i colori per i file `.fss`. In VS Code,
apri quella cartella e premi **F5** per avviare un host di sviluppo
dell'estensione; nella nuova finestra apri un file `.fss`.

## Contenuto del progetto

- `fusionlocks.py` — interprete e strumento da riga di comando.
- `run-fusionlocks.bat` — avviatore portabile per Windows.
- `examples/` — esempi funzionanti in inglese e italiano.
- `tests/` — test automatici dell'interprete.
- `vscode-extension/` — supporto del linguaggio in VS Code.
- `logo.svg` — logo vettoriale originale del progetto.

Per eseguire i test con Python 3:

```bat
python -m unittest discover -s tests -v
```

## Licenza e condizioni

FusionLocks e distribuito con la [licenza MIT](LICENSE), che descrive permessi
e condizioni per il codice di questo progetto. Non esistono Termini di
servizio separati per FusionLocks: questo repository e un programma, non un
servizio online. Python e VS Code sono progetti distinti, con licenze e note
proprie: consulta i loro siti ufficiali per quelle condizioni.

## Pubblicare su GitHub

Crea un repository vuoto chiamato `FusionLocks` su
[github.com/new](https://github.com/new) (non creare prima un README o una
licenza). Apri PowerShell in questa cartella ed esegui i comandi seguenti,
sostituendo il segnaposto con il tuo nome utente GitHub:

```powershell
git init
git add .
git commit -m "Initial FusionLocks language"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/FusionLocks.git
git push -u origin main
```

Non caricare su GitHub il runtime privato di Python: `.gitignore` esclude
`runtime/`.

## Contributi

Sono benvenute segnalazioni e proposte tramite issue e pull request. Quando
proponi una funzione del linguaggio, includi un piccolo esempio `.fss` e i
relativi test. Questa e una versione iniziale: sintassi e comportamento
potranno evolvere.
