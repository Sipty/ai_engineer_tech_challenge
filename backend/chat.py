from haystack.nodes import PromptNode, PromptTemplate
from haystack.pipelines import Pipeline
from datasets import load_dataset

class Chat:
    def __init__(self) -> None:     
        # Load the SQuAD dataset
        self.pipeline = Pipeline()
        self.squad_dataset = load_dataset("squad", split="train")

        # Initialize the PromptNode with GPT-Neo-1.3B
        prompt_node = PromptNode(model_name_or_path="EleutherAI/gpt-neo-125M",
                                max_length=256,
                                use_gpu=False)
        
        # Create a simple pipeline
        self.pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Query"])

    def __produce_relevant_examples(self, query, num_examples=1):
        query_words = set(query.lower().split())
        
        def score_example(example):
            question_words = set(example['question'].lower().split())
            context_words = set(example['context'].lower().split())
            question_score = len(query_words & question_words)
            context_score = len(query_words & context_words)
            return question_score * 2 + context_score

        scored_examples = sorted(
            [(score_example(ex), ex) for ex in self.squad_dataset if score_example(ex) > 0],
            key=lambda x: x[0],
            reverse=True
        )[:num_examples]

        formatted_examples = []
        for i, (_, ex) in enumerate(scored_examples, 1):
            answer_text = ex['answers']['text'][0]
            formatted_example = f"""Example {i}:
                Q: {ex['question']}
                A: {answer_text}
            """
            formatted_examples.append(formatted_example)

        return "\n\n".join(formatted_examples)

    def __trim_incomplete_sentences(self, s):
        punctuation = set('.!')
        for i in range(len(s)):
            if s[i] in punctuation:
                return s[:i+1]
        return s

    def message(self, input):
        print("Message %s received. Preparing response response...", input)           
        # Get and format relevant examples from the dataset
        examples = ""#self.__produce_relevant_examples(input)
        
        # Create a new PromptTemplate for each query
        prompt_template = PromptTemplate(prompt=f"""
            Given the following examples and their contexts, answer the question.
            {examples}
            Question: {{query}}
            Provide a concise and accurate answer to the question based on the given examples and their contexts.
            If the examples don't provide enough information to answer the question confidently, say so.
            Answer:
        """)
        
        # Run the pipeline
        result = self.pipeline.run(
            query=input,
            params={
                "PromptNode": {
                    "prompt_template": prompt_template
                }
            }
        )
        
        response = self.__trim_incomplete_sentences(result["results"][0])
        print("Chatbot:", response)
        return response


# Initialize Chat once and hold it in memory
chat = Chat()

def get_chat_response(input):
    return chat.message(input)