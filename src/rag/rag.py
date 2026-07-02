import src.pipeline.pipeline as pipeline
import src.llm.callToLLM as callToLLM
import src.bdController.bdController as bdController

class rag():
    def __init__(self, delete=False, unificate=False, threshold=0):
        self.BD = bdController.bdController()
        self.nRetrieval=5
        self.delete_derrogations=delete
        self.unificated_versions=unificate
        self.min_theshold=threshold
        

    def newBoeDocument(self, idDocument: str)-> None:
        #Ejecutamos el pipeline
        out, art_unificated, art_delete, files_delete = pipeline.pipeline(idDocument, self.BD,  self.delete_derrogations, self.unificated_versions)

        if out==True:
            print(f"Articulos unificados = {art_unificated}")
            print(f"Articulos derrogados = {art_delete}")
            print(f"Documentos derrogados = {files_delete}")
            print(f"OK: {idDocument}")
            return True
        else:
            print(f"Error: {idDocument}")
            return False
        
    def newListBoesDocuments(self, idsDocuments):
        all_art_unificated = 0
        all_art_delete = 0 
        all_files_delete = 0
        for doc in idsDocuments:
            out, art_unificated, art_delete, files_delete = pipeline.pipeline(doc, self.BD,  self.delete_derrogations, self.unificated_versions)
            all_art_unificated += art_unificated
            all_art_delete += art_delete
            all_files_delete += files_delete
            if out==True:
                print(f"OK: {doc}")
            if out==False:
                print(f"Error: {doc}")
                return False
        print(f"Articulos unificados = {all_art_unificated}")
        print(f"Articulos derrogados = {all_art_delete}")
        print(f"Documentos derrogados = {all_files_delete}")
        return True

    def purgarBasesDatos(self)-> None:
        self.BD.purge()
    
    def deleteDocument(self, id_documento: str)-> None:
        print(self.BD.deleteDocument(id_documento))
    
    def print_all_document(self)-> list[str]:
        resultados = self.BD.listDocuments()
        if resultados is None:
            return []
        return resultados

    def preguntar(self, query: str, is_testing=False)-> str:
        #Obtenemos los documentos de la BD
        texts=self.BD.retrieval(query, self.nRetrieval, self.min_theshold)

        #llamamos al llm
        if is_testing:
            return callToLLM.make_rag_question(query, texts), texts
        else:
            return callToLLM.make_rag_question(query, texts)

    def change_min_theshold(self, theshold):
        self.min_theshold=theshold

    def changeMinThreshold(self, threshold):
        self.min_theshold=threshold

    def change_top_k(self, new_top):
        self.nRetrieval=new_top
        