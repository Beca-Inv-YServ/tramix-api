"""
Script para cargar los datos iniciales (semilla) en la base de datos.

Corre con:
    python -m app.seed_data

Los 5 tramites tienen contenido real, verificado en fuentes oficiales
(argentina.gob.ar, anses.gob.ar, cordoba.gob.ar / registrocivil.cba.gov.ar)
al momento de armar este seed. Cada Chunk viene de una FuenteOficial puntual, 
y esa es la unica fuente que el RAG puede citar para ese tramite.
"""
from app.database import Base, SessionLocal, engine
from app.models import Chunk, OfficialSource, Procedure, Requirement
from app.services.gemini_client import embed_text

# ---------------------------------------------------------------------------
# 1) Metadata de los 5 trámites
# ---------------------------------------------------------------------------

PROCEDURES_SEED = [
    {
        "name": "Renovación de licencia de conducir",
        "short_description": "Renovación de la licencia de conducir particular (autos y motos) en la ciudad de Córdoba.",
        "category": "municipal",
        "agency": "Municipalidad de Córdoba",
    },
    {
        "name": "Duplicado de DNI",
        "short_description": "Nuevo ejemplar de DNI por robo, extravío, deterioro o vencimiento.",
        "category": "nacional",
        "agency": "RENAPER",
    },
    {
        "name": "Partida de nacimiento",
        "short_description": "Solicitud de copia de partida de nacimiento inscripta en la Provincia de Córdoba.",
        "category": "provincial",
        "agency": "Registro Civil de la Provincia de Córdoba",
    },
    {
        "name": "Patentamiento vehicular",
        "short_description": "Inscripción inicial de un vehículo 0km o usado en el Registro del Automotor.",
        "category": "nacional",
        "agency": "Registro Nacional de la Propiedad del Automotor (DNRPA)",
    },
    {
        "name": "Asignación Universal por Hijo",
        "short_description": "Solicitud y requisitos de la Asignación Universal por Hijo (AUH).",
        "category": "nacional",
        "agency": "ANSES",
    },
]

# ---------------------------------------------------------------------------
# 2) Contenido real por tramite: fuente oficial + requisitos + chunks
#    (mismo patron para los 5)
# ---------------------------------------------------------------------------

CONTENT_BY_PROCEDURE = {
    "Renovación de licencia de conducir": {
        "source": {
            "title": "Mi Licencia Digital – Trámites, Municipalidad de Córdoba",
            "url": "https://cordoba.gob.ar/mi-licencia-digital-tramites/",
        },
        "requirements": [
            "DNI con domicilio en la ciudad de Córdoba",
            "Licencia de conducir anterior (vigente o vencida hasta 2 años)",
            "Declaración Jurada de Salud y Certificado Médico de aptitud psicofísica",
            "Boleta de CENAT paga (válida por 60 días)",
            "Aprobar el examen teórico online (en INFOSSEP)",
        ],
        "chunks": [
            (
                "Para renovar la licencia de conducir particular en la Municipalidad de "
                "Córdoba, la persona debe tener domicilio dentro del ejido municipal "
                "(acreditado con el DNI) y su licencia anterior debe ser de tipo "
                "nacional, con no más de 2 años de vencida. No se puede ampliar la "
                "categoría de la licencia por medio de una renovación."
            ),
            (
                "Los pasos para renovar son: aprobar el examen teórico online "
                "disponible en INFOSSEP, ingresar a 'Mi Licencia Digital' en VeDi y "
                "completar la solicitud de renovación, adjuntar la Declaración "
                "Jurada de Salud y el Certificado Médico de aptitud psicofísica "
                "firmado por un médico particular, adjuntar la boleta de CENAT "
                "pagada, y luego reservar un turno digital para retirar la licencia "
                "en uno de los CPC habilitados."
            ),
            (
                "La boleta de CENAT tiene una validez de 60 días desde que se paga. "
                "El costo del trámite es variable, depende de la categoría de la "
                "licencia y de la cantidad de años que se solicite. Al momento de "
                "retirar la licencia en el CPC, se vuelve a controlar que la "
                "persona no esté inhabilitada para conducir por infracciones de "
                "tránsito sin resolver, en cualquier jurisdicción (municipal, "
                "provincial o nacional)."
            ),
        ],
    },
    "Duplicado de DNI": {
        "source": {
            "title": "Tramitar un nuevo ejemplar de DNI, Argentina.gob.ar",
            "url": "https://www.argentina.gob.ar/servicio/tramitar-un-nuevo-ejemplar-de-dni",
        },
        "requirements": [
            "DNI anterior, si todavía se conserva",
            "Denuncia de robo o extravío, si corresponde",
            "Turno en Registro Civil o Centro de Documentación RENAPER",
        ],
        "chunks": [
            (
                "El trámite de nuevo ejemplar de DNI se hace si cambiaste de "
                "domicilio, perdiste el documento, se te venció, necesitás "
                "canjearlo, te lo robaron, o sufrió algún deterioro. Para mayores "
                "de 14 años: si todavía tenés tu DNI anterior, llevalo; si lo "
                "extraviaste o te lo robaron y tenés la denuncia, llevala también. "
                "Ninguno de estos requisitos es excluyente entre sí."
            ),
            (
                "Para hacer el trámite hay que elegir el Registro Civil más "
                "cercano al domicilio, o sacar turno para un Centro de "
                "Documentación RENAPER a través de la app Mi Argentina, y "
                "presentarse en la oficina elegida con la constancia de turno si "
                "corresponde. Es importante guardar la constancia de solicitud "
                "del trámite para poder hacer el seguimiento online."
            ),
            (
                "El nuevo DNI llega por correo al domicilio declarado (lo puede "
                "recibir el titular o una persona mayor de 18 años con la "
                "constancia del trámite), o se puede retirar en la oficina "
                "presentando esa misma constancia. El trámite demora 15 minutos "
                "una vez en la oficina, tiene un costo de $10.000, y el nuevo "
                "ejemplar tiene una vigencia de 15 años para mayores de 14 años."
            ),
        ],
    },
    "Partida de nacimiento": {
        "source": {
            "title": "Solicitud de Partidas - Registro Civil, Gobierno de Córdoba",
            "url": "https://registrocivil.cba.gov.ar/solicitud-partidas/",
        },
        "requirements": [
            "Cuenta de Ciudadano Digital (CiDi) nivel 2",
            "Datos de la persona: nombre, fecha y lugar de nacimiento",
            "Datos del acta si se conocen (tomo, serie, folio, año) — acelera la búsqueda",
            "Indicar si se necesita legalizada (para presentar fuera de Córdoba)",
        ],
        "chunks": [
            (
                "La solicitud de copias de partidas de nacimiento (también "
                "matrimonio, defunción y uniones convivenciales) inscriptas en la "
                "Provincia de Córdoba se inicia de manera digital, en el servicio "
                "'Mi Registro Civil' de la plataforma Ciudadano Digital (CiDi). "
                "Para poder solicitarla es necesario contar con una cuenta de "
                "CiDi nivel 2."
            ),
            (
                "Para pedir el acta hay que completar los datos de la persona "
                "sobre la que se solicita, indicar el motivo de la solicitud, y "
                "si corresponde, marcar la opción 'Legalizada' cuando el acta se "
                "va a presentar fuera de la Provincia de Córdoba. Cuantos más "
                "datos se puedan aportar (localidad original de inscripción, "
                "tomo, serie, folio y año del acta), más rápida es la búsqueda."
            ),
            (
                "Una vez enviada la solicitud, llega un cupón de pago por mail. "
                "Acreditado el pago, el acta se entrega de forma digital en la "
                "sección 'Mis documentos' de CiDi. Según la ley impositiva "
                "vigente, la copia de acta o certificado de nacimiento pedida "
                "específicamente para un trámite de identificación (DNI), y la "
                "primera copia de acta de matrimonio, no tienen costo."
            ),
        ],
    },
    "Patentamiento vehicular": {
        "source": {
            "title": "Inscribir por primera vez el dominio de un automotor, Argentina.gob.ar",
            "url": "https://www.argentina.gob.ar/servicio/inscribir-por-primera-vez-el-dominio-de-un-automotor",
        },
        "requirements": [
            "DNI (original y fotocopia o copia certificada)",
            "Constancia de CUIL, CUIT o CDI",
            "Formulario 12 de Verificación Policial del Vehículo (válido 150 días hábiles)",
            "Certificado de fabricación o de importación, según el origen",
            "Solicitud Tipo 01 (Nacional o Importado), completada y firmada",
            "Factura de compra original y fotocopia",
        ],
        "chunks": [
            (
                "La inscripción inicial de un automotor (patentamiento) permite "
                "anotar el dominio de un 0km o de un vehículo, moto o maquinaria "
                "vial que no fue inscripto con anterioridad. Es obligatoria: sin "
                "esta inscripción no se puede circular con el vehículo. La puede "
                "hacer el comprador, la concesionaria/agencia, o un tercero que "
                "medie entre ambos."
            ),
            (
                "La documentación necesaria incluye: DNI original y copia (o "
                "pasaporte para extranjeros sin residencia), constancia de "
                "CUIL/CUIT/CDI, el Formulario 12 de Verificación Policial del "
                "Vehículo (tiene una validez de 150 días hábiles), el certificado "
                "de fabricación o de importación según el origen del vehículo, la "
                "Solicitud Tipo 01 correspondiente debidamente firmada, y la "
                "factura de compra original."
            ),
            (
                "El trámite se hace en el Registro Automotor que corresponde al "
                "domicilio del comprador: se entrega toda la documentación y se "
                "completa el formulario 13 en el lugar. A las 48 horas de "
                "entregada la documentación se pueden retirar las chapas patente. "
                "El costo es de 1,5% del valor del vehículo si es de origen "
                "nacional, o 2% si es importado, más gastos de cédula, placa y "
                "sellos provinciales."
            ),
        ],
    },
    "Asignación Universal por Hijo": {
        "source": {
            "title": "Asignación Universal por Hijo, ANSES",
            "url": "https://www.anses.gob.ar/hijos/asignacion-universal-por-hijo",
        },
        "requirements": [
            "DNI del titular a cargo y del hijo/a",
            "Certificado o partida de nacimiento del hijo/a",
            "Certificado de matrimonio, unión civil o convivencia (si corresponde)",
            "Vínculos familiares actualizados en Mi ANSES",
        ],
        "chunks": [
            (
                "La Asignación Universal por Hijo (AUH) es automática: no hace "
                "falta iniciar un trámite si ya se cumplen los requisitos y los "
                "vínculos familiares están acreditados en ANSES. El primer paso "
                "es entrar a 'Mi ANSES' y revisar que los datos personales, de "
                "contacto, y los vínculos familiares estén actualizados."
            ),
            (
                "Los requisitos son: ser argentino/a y residir en el país (si es "
                "extranjero/a o naturalizado/a, se exige un mínimo de 2 años de "
                "residencia), que el hijo/a sea soltero/a y menor de 18 años (sin "
                "límite de edad si tiene discapacidad), contar con el DNI del "
                "titular y del hijo/a, y tener el certificado o partida de "
                "nacimiento correspondiente."
            ),
            (
                "Si los vínculos familiares no figuran actualizados, se pueden "
                "corregir a través del canal de Atención Virtual de ANSES, "
                "presentando la documentación respaldatoria: partidas de "
                "nacimiento de los hijos, certificado de matrimonio o "
                "convivencia, y los DNI de todo el grupo familiar. Una vez "
                "acreditados los vínculos y cumplidos los requisitos, el cobro "
                "empieza de forma automática."
            ),
        ],
    },
}


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Procedure).count() > 0:
            print("Ya hay tramites cargados, no se vuelve a sembrar. Borra la tabla si queres reiniciar.")
            return

        for data in PROCEDURES_SEED:
            procedure = Procedure(**data)
            db.add(procedure)
            db.flush()  # para obtener el id sin hacer commit todavia

            content = CONTENT_BY_PROCEDURE[data["name"]]

            for i, description in enumerate(content["requirements"]):
                db.add(Requirement(procedure_id=procedure.id, description=description, order=i))

            source = OfficialSource(procedure_id=procedure.id, **content["source"])
            db.add(source)
            db.flush()

            print(f"Generando embeddings con Gemini para '{data['nombre']}'...")
            for chunk_text in content["chunks"]:
                vector = embed_text(chunk_text, task_type="RETRIEVAL_DOCUMENT")
                db.add(Chunk(procedure_id=procedure.id, source_id=source.id, content=chunk_text, embedding=vector))

        db.commit()
        print(f"Listo! {len(PROCEDURES_SEED)} tramites fueron cargados, todos con contenido real y una fuente citada.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
