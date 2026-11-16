# Resultados de Evaluación Experimental (Criterio C3 ABET)

- **Context Recall (Tasa de Recuperación Exacta de Manual):** 37.5%
- **Similitud Coseno Promedio:** 0.5864
- **Latencia Promedio por Consulta:** 27.4 ms

## Tabla de Casos de Prueba Evaluados

| ID | Categoria | Consulta | Documento_Esperado | Doc_Recuperado_Top1 | Similitud | Resultado | Latencia_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | BOP-2_Parametros | ¿Cómo se accede al menú de configuración rápi... | bop2_ba20_022016_en_en-us1.pdf | bop2_ba20_022016_en_en-us1.pdf | 0.6172 | ACIERTO | 0.0967 |
| Q02 | BOP-2_Fallos | ¿Qué indica el código de fallo F07900 en un c... | bop2_ba20_022016_en_en-us1.pdf | WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf | 0.482 | FALLO | 0.0193 |
| Q03 | BOP-2_Backup | ¿Es posible clonar o copiar un juego de parám... | bop2_ba20_022016_en_en-us1.pdf | WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf | 0.588 | FALLO | 0.019 |
| Q04 | TIA_Hardware | ¿En qué menú de TIA Portal se realiza la conf... | DE_TIA-PRO1_EN_01_V150000.pdf | WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf | 0.6694 | FALLO | 0.021 |
| Q05 | TIA_Programacion | ¿Cuál es la diferencia fundamental entre un B... | DE_TIA-PRO1_EN_01_V150000.pdf | s71500_cpu1516_3_pn_dp_manual_en-US_en-US.pdf | 0.5251 | FALLO | 0.0217 |
| Q06 | TIA_Diagnostico | ¿Cómo se abre el búfer de diagnóstico (Diagno... | DE_TIA-PRO1_EN_01_V150000.pdf | DE_TIA-PRO1_EN_01_V150000.pdf | 0.6864 | ACIERTO | 0.0192 |
| Q07 | TIA_Organizacion | ¿Qué número de bloque de organización (OB) co... | DE_TIA-PRO1_EN_01_V150000.pdf | DE_TIA-PRO1_EN_01_V150000.pdf | 0.5586 | ACIERTO | 0.0181 |
| Q08 | Caso_Limite_Alucinacion | ¿Cómo se configura un PLC Allen-Bradley Contr... | NONE (Debe rechazar alucinación) | WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf | 0.6269 | RECHAZO_VALIDADO | 0.0199 |
| Q09 | Caso_Limite_Alucinacion | ¿Cuál es la velocidad máxima en radianes por ... | NONE (Debe rechazar alucinación) | WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf | 0.5197 | RECHAZO_VALIDADO | 0.0192 |
| Q10 | TIA_Datos | ¿Qué tamaño en bits y rango tiene el tipo de ... | DE_TIA-PRO1_EN_01_V150000.pdf | WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf | 0.5903 | FALLO | 0.02 |

