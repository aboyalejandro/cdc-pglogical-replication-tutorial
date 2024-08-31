MUST:

- Un repo por proyecto
- Agregar scripts de SQL (a través de Python) que hagan el setup inicial full para CDC, tener en cuenta que se tienen que ejecutar scripts en ambos nodos: 
    - Logical Replication ✅
    - pglogical plugin ✅
    - Airbyte 

- Install Airbyte a la par de la db de prueba.
- Hacer un comando de Makefile para cada setup ✅
- Ver que más falta de WAL params y meterlo en el Dockerfile ✅

NICE:

- Crear las tablas ya con ID serial. Buscar si Faker puede emular esto, como mínimo crearla con PK. ✅
- Preparar repo para que lo puedan usar metiendo sus datos fake o no que simplemente expongan BDs truchas. ✅
- Que se puedan agregar nuevas tablas y hacer inserts si las tablas no son user_profiles, transactions o products. 