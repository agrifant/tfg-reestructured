import src.bdController.chroma_db as chroma
import src.bdController.utils as utils
import src.extractArticulo as ext
import json
import os

class bdController():

    def __init__(self)-> None:
        """
        Constructor que inicializa las dos bases de datos utilizadas:
        - bd_chroma: Conexión a la base de datos vectorial Chroma.
        - boe_ids: Para mantener la cuenta de cuantos documentos diferentes y cuales son tenemos
        """
        self.bd_chroma= chroma.chroma()
        self.boe_ids=self.get_boe_documents_inserted()
    
    def addDocument(self,
        datos_globales: dict, 
        articulos: list[dict],
        disposiciones: list[dict], 
        texto_extra: list[dict])-> bool:

        #Nos quedamos con los metadatos que nos interesan
        campos_global=["id_boe","url_pdf","tipo_norma","fecha_disposicion","titulo", "departamento", "origen_legislativo", "fecha_publicacion", "numero_norma"]
        metadata_global=utils.filtrar_incluir(datos_globales,campos_global)

        #Comprobamos si ya existe el documento
        if self.existDocument(metadata_global["id_boe"]): return False

        ids=[]
        content=[]
        metadata=[]

        campos_ocultar=["id", "cuerpo"]

        for articulo in articulos:
            #Tratamos la metadata
            metadata_articulo = utils.filtrar_excluir(articulo, campos_ocultar)
            combined_metadata = {**metadata_global, **metadata_articulo}
        
            ids.append(articulo["id"])
            content.append(articulo["cuerpo"])
            metadata.append(combined_metadata)

        for disp in disposiciones:
            #Tratamos la metadata
            metadata_articulo = utils.filtrar_excluir(disp, campos_ocultar)
            combined_metadata = {**metadata_global, **metadata_articulo}
            
            ids.append(disp["id"])
            content.append(disp["cuerpo"])
            metadata.append(combined_metadata)

        for text in texto_extra:
            #Tratamos la metadata
            metadata_articulo = utils.filtrar_excluir(text, campos_ocultar)
            combined_metadata = {**metadata_global, **metadata_articulo}

            ids.append(text["id"])
            content.append(text["cuerpo"])
            metadata.append(combined_metadata)

        if self.bd_chroma.createNodes(ids,content, metadata):
            self.boe_ids.add(metadata_global["id_boe"])
            self.save_boe_documents_inserted()
            return True
        return False

    def deleteDocument(self, documento_id:str)->bool:
        if self.bd_chroma.deleteDocument(documento_id):
            self.boe_ids.discard(documento_id)
            self.save_boe_documents_inserted()
            return True
        return False

    def deleteFromMetadata(self, data):
        try:
            if not data:
                return False
    
            eliminate_all_norma = False
    
            # Si solo hay una condición
            if len(data) == 1:
                where_clause = data[0]
    
                if where_clause.get("numero_norma"):
                    eliminate_all_norma = True
            else:
                where_clause = {"$and": data}
    
            delete = self.bd_chroma.deleteFromMetadata(where_clause)
    
            if delete is not None and eliminate_all_norma:
                self.boe_ids.discard(delete)
                self.save_boe_documents_inserted()
    
            return delete
    
        except Exception as e:
            print(f"Error en deleteFromMetadata: {e}")
            return None

    def purge(self)->bool:
        if self.bd_chroma.purge():
            self.boe_ids = set()
            self.save_boe_documents_inserted()
            return True
        return False

    def listDocuments(self):
        boes_inserted=self.get_boe_documents_inserted()
        return list(boes_inserted)

    def retrieval(self, query, n):
        ids, scores = self.bd_chroma.semanticSearch(query, n)
        score_map = {i: s for i, s in zip(ids, scores)}

        articulos = ext.extract_articulos_more_than_one(query)

        if articulos:
            for art in articulos:
                where_filter = {"num_articulo": art}
                ids_filtered, scores_filtered = self.bd_chroma.semanticSearchArticle(
                    query, where_filter, n
                )

                for i, s in zip(ids_filtered, scores_filtered):
                    if i in score_map:
                        score_map[i] += 0.2  
                    else:
                        score_map[i] = s + 0.2


        final_ids = sorted(score_map, key=score_map.get, reverse=True)[:n]

        data = self.bd_chroma.getDataNode(final_ids) if final_ids else []
        return "\n\n".join(data)

    def existDocument(self, id_boe: str) -> bool:
        return id_boe in self.boe_ids

    def get_boe_documents_inserted(self) -> set[str]:
        try:
            if not os.path.exists("src/bdController/boes_ids.json"):
                return set()

            with open("src/bdController/boes_ids.json", "r") as f:
                data = json.load(f)
                return set(data)

        except Exception as e:
            print(f"Error cargando src/bdController/boes_ids.json: {e}")
            return set()
    
    def save_boe_documents_inserted(self):
        try:
            with open("src/bdController/boes_ids.json", "w") as f:
                json.dump(list(self.boe_ids), f)

        except Exception as e:
            print(f"Error guardando src/bdController/boes_ids.json: {e}")