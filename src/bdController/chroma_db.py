import chromadb
from . import embeding as embedding
# chroma run --host localhost --port 8001

class chroma():
    def __init__(self) -> None:
        self.collection_name = "rag_legislacion"

        #Cliente HTTP
        self.client = chromadb.HttpClient(
            host="localhost",
            port=8001
        )

        self.get_collection()

    def get_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name
        )
    
    #CREATE
    def createNodes(self, ids:list[str], content:list[str], metadata:list[str], dim:int) -> bool:
        try:
            collection = self.get_collection()

            # embeddings
            content_embedded = embedding.content_to_embedding(content, dim)

            collection.add(
                ids=ids,
                documents=content,
                embeddings=content_embedded,
                metadatas=metadata
            )

            return True

        except Exception as e:
            print(f"Error creando relaciones: {e}")
            return False

    #DELETE
    def purge(self) -> bool:
        try:
            #self.client.reset()
            self.client.delete_collection(self.collection_name)
        except Exception as e:
            print(f"Error purgando base de datos: {e}")
            return False

        self.client.get_or_create_collection(self.collection_name)
        return True

    def changeMetadata(self, data, type_metadata, new_value):
        try:
            if not data:
                return False, 0
    
            # 1. Build where
            if len(data) == 1:
                where_clause = data[0]
            else:
                where_clause = {"$and": data}
    
            collection = self.get_collection()
    
            # 2. Get docs
            results = collection.get(
                where=where_clause,
                include=["metadatas"]
            )
    
            ids = results.get("ids", [])
            metadatas = results.get("metadatas", [])
    
            # 3. Safety check (IMPORTANTE)
            if not ids or not metadatas:
                return False
    
            # 4. Update metadata
            new_metadatas = [
                {**meta, type_metadata: new_value}
                for meta in metadatas
            ]
    
            # 5. Update Chroma
            collection.update(
                ids=ids,
                metadatas=new_metadatas
            )
    
            return True
    
        except Exception as e:
            print(f"Error cambiando metadata: {e}")
            return False , 0

    def deleteFromMetadata(self, where):
        try:
            collection = self.get_collection()
    
            existing = collection.get(where=where)
    
            ids_before = existing.get("ids", [])
            if not ids_before:
                return None
    
            # Obtener el id_boe del primer documento
            metadatas = existing.get("metadatas", [])
            id_boe = metadatas[0].get("id_boe") if metadatas else None
    
            collection.delete(where=where)
    
            print(f"Eliminado: {where}")
            return id_boe
    
        except Exception as e:
            print(f"Error eliminando documento: {e}")
            return None
    
    def deleteDocument(self, id_document: str) -> bool:
        return self.deleteFromMetadata({"id_boe": id_document})

    #SEARCH/OTHER   
    def semanticSearch(self, query: str, n_results,  dim) -> tuple[list[str], list[float]]:
        try:
            collection = self.get_collection()

            query_embedding = embedding.content_to_embedding([query], dim)

            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                 where={"estado": "vigente"},
                include=["distances"]
            )

            ids = results["ids"][0]
            distances = results["distances"][0]

            similarities = [1 / (1 + d) for d in distances]
            return ids, similarities

        except Exception as e:
            print(f"Error en la consulta: {e}")
            return [], []

    def semanticSearchArticle(self, query: str, where_filter, n_results: int, dim)-> tuple[list[str], list[float]]:
        try:
            base_conditions = []

            if where_filter:
                base_conditions.append(where_filter)
            
            base_conditions.append({"estado": "vigente"})
            
            where = {"$and": base_conditions}
            
            collection = self.get_collection()

            query_embedding = embedding.content_to_embedding([query], dim)

            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["distances"],
                where=where
            )

            ids = results["ids"][0]
            distances = results["distances"][0]

            similarities = [1 / (1 + d) for d in distances]
            return ids, similarities

        except Exception as e:
            print(f"Error en la consulta: {e}")
            return [], []
    
    def countNodes(self)-> int:
        collection = self.get_collection()
        return  collection.count()

    def getDataNode(self, ids: list[str]) -> str:
        collection = self.get_collection()

        results = collection.get(ids=ids)

        metadatas = results.get("metadatas", [])

        out = []

        for i in range(len(metadatas)):
            iter=[]
            ley = metadatas[i].get("numero_norma", "")
            url = metadatas[i].get("url_pdf", "")
            titulo_norma = metadatas[i].get('titulo_norma')
            titulo = metadatas[i].get('titulo',"Preambulo")
            cuerpo = metadatas[i].get('cuerpo_integro')

            iter.append(f"{ley} {titulo_norma} {titulo}\n{url}\n")
            iter.append(cuerpo)
            doc="".join(iter)
            out.append(doc)

        return out

    def get_node_metadata(self, base_conditions):
        where = {"$and": base_conditions}
        collection = self.get_collection()
    
        result = collection.get(
            where=where,
            include=["metadatas"]
        )
    
        return result