# Hoja de ruta — Entrega 1

Reparto de tareas del TP Integrador (EcoLogix Systems). El esqueleto del proyecto ya está en el
repo y los tests pasan. Lo que falta es lo que ningún código puede hacer solo: pegar evidencia
real, tomar decisiones y poder defenderlas en la oral.

**Cómo usar este archivo:** cuando termines tu tarea, editá este archivo en GitHub (ícono del
lápiz), cambiá tu `- [ ]` por `- [x]` y commiteá. Eso deja constancia de quién la hizo y cuándo.

---

## 1. Setup (una sola vez, todos)

Lo hacen todos, incluidos los que tienen una tarea de escritura. Ninguno de estos comandos
consume créditos de API.

```bash
# 1. Clonar (después de aceptar la invitación al repo)
git clone https://github.com/LDibiase/dsi-tp-integrador.git
cd dsi-tp-integrador

# 2. Identificarse con el MISMO mail de la cuenta de GitHub
#    (sin esto los commits no se asocian a tu usuario y la cátedra no ve quién hizo qué)
git config user.name "Nombre Apellido"
git config user.email "mail@de.github"

# 3. Entorno virtual
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 4. Dependencias
pip install -r requirements.txt

# 5. Verificar que quedó bien -> tiene que decir "12 passed"
pytest -q test_schemas.py
*python -m pytest -q test_schemas.py --- Por si el otro no funciona*
```

Si el paso 5 dice cualquier otra cosa, avisá en el grupo antes de seguir.

---

## 2. Ciclo para subir un cambio

Esto se repite en cada tarea. El `pull --rebase` del principio evita el 90% de los problemas.

```bash
git pull --rebase                  # traer lo que subieron los demás — SIEMPRE primero
# ... editar el archivo ...
git add informe.md
git commit -m "docs(informe): describí acá qué hiciste"
git push
```

Si el `push` es rechazado, alguien subió algo en el medio: `git pull --rebase` y `git push` otra
vez. Si el rebase marca **conflicto** en `informe.md`, pará y avisá en el grupo antes de tocar nada.

---

## 3. Para todos

Dos ediciones de una línea cada una. Conviene hacerlas en **commits separados**.

- [ ] **T-00a — Agregar tu nombre en el README** · *cada integrante*
  - Buscar la línea `**Grupo:** ⚠️ completar…` y agregar nombre, usuario de Git y la parte que vas a liderar.
  - **Dónde:** `README.md`, línea 4
  - **Commit:** `docs: agrega <nombre> a integrantes del README`

- [ ] **T-00b — Agregar tu nombre en el informe** · *cada integrante*
  - Lo mismo en la línea `**Integrantes:** ⚠️ completar…` del encabezado.
  - **Dónde:** `informe.md`, línea 5
  - **Commit:** `docs(informe): agrega <nombre> a integrantes`

---

## 4. Tareas asignadas

Propuesta de reparto, ajustable. Los usuarios son los del repo; a medida que cada uno se
identifique en el README les vamos poniendo nombre.

- [x] **T-01 — Evidencia A.2, primer modelo** · `@Fedoh` · 15 min
  - Abrir ChatGPT, Claude o Gemini **sin darle ningún catálogo ni base de datos** y pegar el prompt
    que ya está escrito en la sección A.2. Después pegar la respuesta **textual** en el informe y
    marcar lo que el modelo inventó: precios, stock, plazos de entrega. Ese invento es la evidencia
    de por qué el sistema necesita una base de datos como autoridad.
  - **Dónde:** `informe.md` § A.2, buscar el ⚠️ (líneas 19-38)
  - **Entrega:** la respuesta pegada + completar "Con qué nivel de confianza lo presentó"
  - **Commit:** `docs(informe): evidencia A.2 con alucinaciones marcadas`

- [x] **T-02 — Evidencia A.2, segundo modelo** · `@Folguee` · 15 min
  - El mismo prompt que T-01 pero en otro modelo, para comparar. La sección pide justamente que dos
    integrantes lo prueben con modelos distintos y elijan la evidencia más clara. Coordinar con
    quien tome T-01 para no usar el mismo.
  - **Dónde:** `informe.md` § A.2
  - **Entrega:** segunda respuesta pegada; entre los dos eligen cuál queda
  - **Commit:** `docs(informe): segunda evidencia A.2 para comparar`

- [ ] **T-03 — Elegir la hipótesis más riesgosa (B.7)** · `@LuciaLG1988` · 20 min
  - Hay dos hipótesis redactadas y queda una sola. La primera dice que el stock del depósito se
    puede actualizar en tiempo real; la alternativa dice que los clientes describen los productos
    con precisión suficiente para mapearlos al catálogo. Elegir cuál es más riesgosa *para este
    negocio* y borrar la otra o bajarla a nota al pie.
  - **Dónde:** `informe.md` § B.7, línea 296
  - **Entrega:** una sola hipótesis en firme, con el porqué de la elección
  - **Commit:** `docs(informe): elige hipótesis más riesgosa de B.7`

- [x] **T-04 — Defender o bajar el riesgo de `SEGUIMIENTO_PEDIDO`** · `@martaza-ort` · 20 min
  - Hoy lo marcamos **MEDIO**: es una lectura, pero de datos de un tercero, y sin verificar
    titularidad se filtra el pedido de otro cliente. La cátedra tiende a marcar toda lectura como
    BAJO. Decidir si lo defendemos con ese argumento o lo bajamos, y dejarlo escrito con su
    fundamento.
  - **Dónde:** `informe.md` § B.3 (tabla) + "Decisiones abiertas" #4
  - **Entrega:** decisión escrita, con el mismo formato que ya tiene el punto 2
  - **Commit:** `docs(informe): fundamenta el riesgo de SEGUIMIENTO_PEDIDO`

- [x] **T-05 — Fundamentar los tres umbrales** · `@agustinasalatino` · 25 min
  - Confianza mínima **0.60** para no derivar a un humano, cantidad máxima **10.000** por línea de
    pedido, número de pedido de **4 a 8 dígitos**. Los tres están inventados. No hace falta un
    número perfecto: hace falta poder contestar "¿por qué 0.60?" en la oral. Un fundamento honesto
    sirve — por ejemplo, que es el default de la cátedra, que sin datos de uso no hay con qué
    moverlo, y que se valida con la primera corrida real.
  - **Dónde:** `informe.md` "Decisiones abiertas" #3
  - **Entrega:** un fundamento por umbral, aunque sea provisorio
  - **Commit:** `docs(informe): fundamenta umbrales de confianza y cantidad`

- [x] **T-06 — C.3: correr el lote y pegar la tabla real** · `@LDibiase` · ⚠️ necesita API key
  - Correr los 6 inputs del dominio con few-shot y reemplazar el placeholder de
    `resultados_lote.md` por la tabla generada. Después completar la lectura de los resultados.
  - **Comando:** `python lote.py`
  - **Dónde:** `resultados_lote.md` + `informe.md` § C.3
  - **Commit:** `docs(lote): resultados reales del lote few-shot - C.3`

- [x] **T-07 — C.4: comparar zero-shot contra few-shot** · `@LDibiase` · ⚠️ necesita API key
  - Correr el mismo lote sin ejemplos y comparar las dos tablas. Esperamos diferencia en el caso #5
    (el pedido ambiguo, donde zero-shot tiende a inventar un ítem para "completar") y en el #6 (el
    intento de injection, que zero-shot puede clasificar como `SEGUIMIENTO_PEDIDO` por el número
    4521). Si ningún caso difiere, eso también es un resultado y hay que decirlo.
  - **Comando:** `python lote.py --tecnica zero --salida resultados_lote_zero.md`
  - **Dónde:** `informe.md` § C.4, línea 335
  - **Entrega:** un caso documentado: el input, la salida zero-shot y la few-shot
  - **Commit:** `docs(informe): comparativa zero-shot vs few-shot - C.4`

---

## 5. Para la primera reunión

Estas no tienen dueño: se deciden entre todos y las escribe quien esté a mano.

- [x] **T-08 — Realismo del caso** · *grupal*
  - ¿Alguien conoce un negocio parecido para robarle detalles reales — unidades por bulto, mínimos
    de compra, zonas de entrega? Un detalle real vale más que tres inventados. Si nadie tiene, se
    confirma que queda inventado y listo.
  - **Dónde:** `informe.md` § A.1 + "Decisiones abiertas" #1

- [ ] **T-09 — Repartir la defensa oral** · *grupal*
  - Un integrante por parte: A (caso, evidencia, PEAS, tokens) · B (matriz, decisión técnica,
    artefactos) · C (código, lote, prompting). Pueden preguntarle a cualquiera sobre cualquier
    parte, así que conviene que todos hayan visto el pipeline correr al menos una vez.
  - **Dónde:** `informe.md` "Decisiones abiertas" #7

- [x] **T-10 — Costo en pesos o dólares (opcional)** · `@giaramayo` · *grupal*
  - A.4 deja el cálculo en tokens porque los precios cambian. Si lo quieren en plata, buscar el
    precio vigente por millón de tokens de `gpt-4o-mini` y multiplicar.
  - **Dónde:** `informe.md` § A.4, línea 76

---

## 6. Cuatro reglas que no se rompen

1. **El archivo `.env` nunca se sube.** Ahí va la API key de cada uno. Ya está en `.gitignore`, así
   que alcanza con no forzarlo. Una key en el historial del repo cuesta **−15 puntos** y hay que
   rotarla.

2. **Avisar en el grupo antes de editar `informe.md`.** Casi todas las tareas caen en ese archivo.
   No es que un conflicto no se pueda resolver: es que resolverlo a mano es tiempo tirado. Avisar
   al empezar y al pushear alcanza.

3. **Commits chicos, uno por cosa.** La rúbrica penaliza un único commit "entrega final" con todo
   volcado, y evalúa quién hizo qué. Diez commits chicos de seis personas valen más que uno grande
   y perfecto.

4. **La API key no se comparte.** Cada uno saca la suya en `platform.openai.com` → API keys
   (requiere cargar saldo). Correr el lote entero cuesta menos de un centavo de dólar con
   `gpt-4o-mini`. Nunca por WhatsApp.

---

> Las líneas citadas (`informe.md` 296, 335, …) se corren apenas alguien edite más arriba. Si no
> coinciden, buscá la sección o el marcador ⚠️, que son estables.
