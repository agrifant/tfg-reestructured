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
        out = pipeline.pipeline(idDocument, self.BD,  self.delete_derrogations, self.unificated_versions)

        if out==True:
            print("Texto añadido con éxito")
        else:
            print("No se han podido añadir los textos")

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
        