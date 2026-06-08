import pipeline.chunking as chunk

# python3 -m tests.chunking

documento= {
        "titulo_articulo": "Artículo 20. Licencias.",
        "cuerpo": "\nEl trabajador, previa solicitud por escrito, podrá ausentarse del trabajo con derecho a remuneración en los casos que a continuación se relacionan y por la duración que se indica:\na) Dieciocho días naturales en caso de matrimonio, si bien cuando el trabajador lleve en la empresa menos de un año sólo disfrutará de la parte proporcional a tal período respecto de la diferencia entre lo establecido en el ET y el presente Convenio\nb) Tres días naturales en caso de nacimiento de hijo o enfermedad grave o fallecimiento de cónyuge, hijo, padre o madre de uno u otro cónyuge, nietos, abuelos o hermanos; si el trabajador tuviese necesidad de desplazarse fuera de su residencia, el plazo se incrementará por el tiempo necesario para tal desplazamiento y con un límite máximo de cuatro días naturales en total (permanencia y desplazamiento).\nc) Un día por traslado del domicilio habitual.\nd) Por el tiempo indispensable para el cumplimiento de un deber inexcusable de carácter público y personal.\nLas ausencias al trabajo por visita a consulta médica de la Seguridad Social, por el tiempo empleado en ello, y previo permiso de la Empresa, tendrán el carácter de faltas justificadas, si se acreditan debidamente, pero no de permisos abonables.\ne) Para realizar funciones sindicales o de representación del personal y, en los términos establecidos en el convenio siempre que medie la oportuna convocatoria, el permiso de la empresa y la subsiguiente justificación del tiempo utilizado.\nLas licencias a que se refiere el apartado b) se concederán en el acto, sin perjuicio de su posterior justificación, el mismo día de su reincorporación al trabajo. La gravedad de la enfermedad quedará demostrada con justificante de hospitalización o dictamen expreso de un médico. Una misma enfermedad grave solamente dará derecho a un permiso al año.\nLos días de las licencias se iniciarán siempre en día laborable para el trabajador, serán siempre naturales e ininterrumpidos, estando siempre el hecho que motiva el permiso dentro de los días del mismo.\nEstas licencias serán retribuidas con el salario de las tablas del convenio más antigüedad.\nf) Las/os trabajadoras/es, por lactancia de un hijo menor de 9 meses tendrán derecho a una hora de ausencia del trabajo, que podrá dividir en dos fracciones. El titular del derecho, por su voluntad, podrá sustituir este derecho por una reducción de su jornada de media hora con la misma finalidad, sin que pueda transferir este derecho individual al otro progenitor. Cada ocho días laborables se podrán acumular en un día de disfrute completo. La duración del permiso se incrementará proporcionalmente en los casos de parto múltiple. No obstante, si dos personas trabajadras de la misma empresa ejercen este derecho por el mismo sujeto causante, la dirección empresarialpodrá limitar su ejercicio simultáneo por razones justificadas de funcionamiento de la empresa, que deberá comunicar por escrito.\nLas personas que, no habiéndose casado, convivan en unión afectiva y estable, previa justificación de estos extremos mediante certificado de inscripción en el correspondiente registro oficial de parejas de hecho, tendrán las mismas licencias, salvo la establecida en el apartado a), que el resto de los trabajadores/as.",
        "capitulo": "CAPÍTULO VI: Licencias y excedencias",
        "id": "BOE-A-2022-23014_art_21"
    }

documento1={
    "cuerpo": "Vamos a escribir algo relativamente corto para probar\n si corta perfectamentente y si esta función trabajaja como debería tarabar"
}
out=[]
chunk.chunking(documento1["cuerpo"], out, 10, 4, 0.2)

for i in out:
    print("nuevo")
    print(i)
    print("\n\n")