import torch
from tokenizers import BertWordPieceTokenizer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = torch.load("service/baseline/src/fine_tuned_bert_qna.pt")
tokenizer = BertWordPieceTokenizer("service/baseline/src/bert_base_uncased/vocab.txt", lowercase=True)
max_len = 50


# creating input for bert
class Example:
    def __init__(self, question, context, start_char_idx, answer_text, inference=False):
        self.question = question
        self.context = context
        self.start_char_idx = start_char_idx
        self.answer = answer_text
        self.skip = False
        self.inference = inference

    def preprocess(self):
        context = self.context
        question = self.question
        answer_text = self.answer
        start_char_idx = self.start_char_idx

        context = " ".join(str(context).split())
        question = " ".join(str(question).split())
        answer = " ".join(str(answer_text).split())

        end_char_idx = start_char_idx + len(answer)
        if end_char_idx >= len(context):
            self.skip = True
            return

        # Mark the character indexes in context that are in answer
        is_char_in_ans = [0] * len(context)
        for idx in range(start_char_idx, end_char_idx):
            is_char_in_ans[idx] = 1

        tokenized_context = tokenizer.encode(context)

        # Find tokens that were created from answer characters
        ans_token_idx = []
        for idx, (start, end) in enumerate(tokenized_context.offsets):
            if sum(is_char_in_ans[start:end]) > 0:
                ans_token_idx.append(idx)

        if len(ans_token_idx) == 0:
            self.skip = True
            return

        start_token_idx = ans_token_idx[0]
        end_token_idx = ans_token_idx[-1]

        # Tokenize question
        tokenized_question = tokenizer.encode(question)

        input_ids = tokenized_context.ids + tokenized_question.ids[1:]
        token_type_ids = [0] * len(tokenized_context.ids) + [1] * len(
            tokenized_question.ids[1:]
        )
        attention_mask = [1] * len(input_ids)

        # Pad and create attention masks.
        padding_length = max_len - len(input_ids)
        if padding_length > 0:  # pad
            input_ids = input_ids + ([0] * padding_length)
            attention_mask = attention_mask + ([0] * padding_length)
            token_type_ids = token_type_ids + ([0] * padding_length)
        elif padding_length < 0:  # skip
            self.skip = True
            return

        self.input_ids = input_ids
        self.token_type_ids = token_type_ids
        self.attention_mask = attention_mask
        self.start_token_idx = start_token_idx
        self.end_token_idx = end_token_idx
        self.context_token_to_char = tokenized_context.offsets


def create_examples(raw_data):
    squad_examples = []
    for i, row in raw_data.iterrows():
        question = row['question']
        context = row['new_context']
        answer_text = row['answer']
        start_char_idx = row['start_index']
        squad_eg = Example(
            question, context, start_char_idx, answer_text
        )
        squad_eg.preprocess()
        squad_examples.append(squad_eg)
    return squad_examples


def create_inputs_targets(squad_examples, inference=False):
    input_ids = []
    token_type_ids = []
    attention_mask = []
    start_token_idx = []
    end_token_idx = []
    answers = []

    if inference:
        for item in squad_examples:
            if not item.skip:
                input_ids.append(item.input_ids)
                token_type_ids.append(item.token_type_ids)
                attention_mask.append(item.attention_mask)
        return (torch.tensor(input_ids), torch.tensor(token_type_ids), torch.tensor(attention_mask))
    else:

        for item in squad_examples:
            if not item.skip:
                input_ids.append(item.input_ids)
                token_type_ids.append(item.token_type_ids)
                attention_mask.append(item.attention_mask)
                start_token_idx.append(item.start_token_idx)
                end_token_idx.append(item.end_token_idx)
                answers.append(item.answer)

        return (
            torch.tensor(input_ids), torch.tensor(token_type_ids), torch.tensor(attention_mask),
            torch.tensor(start_token_idx), torch.tensor(end_token_idx), answers
        )


def get_attributes(model, tokenizer, object: str, context: str):
    question = f"what are attributes of {object}?"

    squad_eg = Example(question, context, inference=True)
    squad_eg.preprocess()
    input_ids, token_type_ids, attention_mask = create_inputs_targets([squad_eg], inference=True)
    with torch.no_grad():
        input_ids = input_ids.to(device)
        token_type_ids = token_type_ids.to(device)
        attention_mask = attention_mask.to(device)
        start_probs, end_probs = model(input_ids, token_type_ids, attention_mask)

        input_id = input_ids.cpu().numpy()[0]
        pred_start_indices = torch.argmax(start_probs[0]).item()
        pred_end_indices = torch.argmax(end_probs[0]).item()

        # convert tokens to strings
        pred_answer = tokenizer.decode(input_id[pred_start_indices:pred_end_indices + 1], skip_special_tokens=True)

    return pred_answer


def predict_pipeline_dl(js):
    """
    Пайплайн препроцессинга данных и осуществления предсказания
    input: список словарей со значениями objects и contexts
    output: список словарей со значениями objects и attributes
    """
    res = dict()
    for item in js:
        attr = get_attributes(model, tokenizer, item["object"], item["context"])
        res.append({object: attr})
        return res
