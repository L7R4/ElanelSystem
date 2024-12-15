Consigna -> Listar el jugador con mayor goles en el torneo

SELECT TOP 1 j.num_socio, j.nombre, j.apellido, COUNT(g.id_gol) AS TotalGoles
FROM jugador AS j
JOIN gol AS g ON j.num_socio = g.num_socioFK
GROUP BY (j.num_socio)
ORDER BY (TotalGoles) DESC 
