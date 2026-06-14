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
    
    def addDocument(self, articulos: dict, disposiciones:dict, textos_extras:dict, id_boe:str)-> bool:
        #Comprobamos si ya existe el documento
        if self.existDocument(id_boe): return False


        campos_ocultar=["id", "cuerpo"]

        #Guardamos en estos vectores todos los datos que vamos a meter en la bd
        ids=[]
        content=[]
        metadata=[]
        for articulo in articulos:
            #Tratamos la metadata
            metadata_add = utils.filtrar_excluir(articulo, campos_ocultar)
        
            ids.append(articulo["id"])
            content.append(articulo["cuerpo"])
            metadata.append(metadata_add)

        for disposicion in disposiciones:
            #Tratamos la metadata
            metadata_add = utils.filtrar_excluir(disposicion, campos_ocultar)
        
            ids.append(disposicion["id"])
            content.append(disposicion["cuerpo"])
            metadata.append(metadata_add)

        for texto in textos_extras:
            #Tratamos la metadata
            metadata_add = utils.filtrar_excluir(texto, campos_ocultar)
        
            ids.append(texto["id"])
            content.append(texto["cuerpo"])
            metadata.append(metadata_add)

        if self.bd_chroma.createNodes(ids,content, metadata):
            self.boe_ids.add(id_boe)
            self.save_boe_documents_inserted()
            return True
        return False

    def deleteDocument(self, documento_id:str)->bool:
        if self.bd_chroma.deleteDocument(documento_id):
            self.boe_ids.discard(documento_id)
            self.save_boe_documents_inserted()
            return True
        return False

    def changeMetadata(self, data, type_metadata, new_value):
        return self.bd_chroma.changeMetadata(data, type_metadata, new_value)    

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

    def retrieval(self, query, n, threshold):
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
                        score_map[i] *= 1.5  
                    else:
                        score_map[i] = s * 1.5
            
        final_ids = sorted(
            (k for k, v in score_map.items() if v >= threshold),
            key=score_map.get,
            reverse=True
        )[:n]

        data = self.bd_chroma.getDataNode(final_ids) if final_ids else []
        return data

    def get_article(self, ley, article):
        where = [
            {"numero_norma": ley},
            {"num_articulo": article}
        ]
    
        result = self.bd_chroma.get_node_metadata(where)
    
        if not result or not result.get("metadatas", []):
            return None, None
    
        article_parts = []
    
        for metadata in result["metadatas"]:
            article_parts.append(
                (
                    int(metadata.get("parte", 0)),
                    metadata.get("cuerpo_integro", "")
                )
            )
    
        # ordenar por parte
        article_parts.sort(key=lambda x: x[0])
    
        # reconstruir texto completo
        article_complete = "\n".join(texto for _, texto in article_parts)
    
        # devolver también metadata del primer elemento (si existe)
        first_metadata = result["metadatas"][0]
    
        return article_complete, first_metadata

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