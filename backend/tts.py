import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
from snac import SNAC
from unsloth import FastLanguageModel
import scipy.io.wavfile as wavfile

# Load models
print("Loading models...")
lm_model = AutoPeftModelForCausalLM.from_pretrained(
    "/export/fs06/bodoom1/ckpts/lora_model_gh_langs_emotion_last/",
    load_in_4bit=False
)
lm_model = FastLanguageModel.for_inference(lm_model).to("cuda")
tokenizer = AutoTokenizer.from_pretrained(
    "/export/fs06/bodoom1/ckpts/lora_model_gh_langs_emotion_last/"
)
snac_model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").to("cuda")

# Voice mappings
VOICES = {
    "Akuapem": "kwaku",
    "Asante":  "akosua",
    "Ewe":     "mawutor",
    "Hausa":   "tahiru",
}

def redistribute_codes(code_list):
    """Redistribute flat code list into 3-layer hierarchy for SNAC decoder"""
    layer_1, layer_2, layer_3 = [], [], []
    for i in range((len(code_list) + 1) // 7):
        layer_1.append(code_list[7*i])
        layer_2.append(code_list[7*i+1] - 4096)
        layer_3.append(code_list[7*i+2] - 2*4096)
        layer_3.append(code_list[7*i+3] - 3*4096)
        layer_2.append(code_list[7*i+4] - 4*4096)
        layer_3.append(code_list[7*i+5] - 5*4096)
        layer_3.append(code_list[7*i+6] - 6*4096)

    codes = [
        torch.tensor(layer_1).unsqueeze(0).to("cuda"),
        torch.tensor(layer_2).unsqueeze(0).to("cuda"),
        torch.tensor(layer_3).unsqueeze(0).to("cuda"),
    ]
    return snac_model.decode(codes)

def synthesize_speech(text, voice="kwaku", output_file="output.wav", 
                      temperature=0.6, top_p=0.9, repetition_penalty=1.1,
                      max_tokens=2048):
    """
    Synthesize speech from text using specified voice.
    
    Args:
        text: Input text to synthesize
        voice: Voice to use (kwaku, akosua, mawutor, tahiru)
        output_file: Path to save output WAV file
        temperature: Sampling temperature (0.0-1.0)
        top_p: Nucleus sampling parameter (0.0-1.0)
        repetition_penalty: Penalty for repetition (0.5-2.0)
        max_tokens: Maximum tokens to generate
    """
    if voice not in VOICES:
        raise ValueError(f"Voice must be one of: {list(VOICES.keys())}")
    
    # Build prompt
    prompt = f"{voice}: {text}"
    
    # Tokenize
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")[0]
    
    # Pad if too short
    if ids.size(0) < 8:
        pad_len = 15 - ids.size(0)
        pad_tensor = torch.full((pad_len,), 128263, dtype=torch.int64, device="cuda")
        ids = torch.cat([ids, pad_tensor], dim=0)
    
    # Add special tokens
    seq = ids.unsqueeze(0)
    start_tok = torch.tensor([[128259]], dtype=torch.int64).to("cuda")
    end_toks = torch.tensor([[128009, 128260]], dtype=torch.int64).to("cuda")
    seq = torch.cat([start_tok, seq, end_toks], dim=1)
    
    # Generate
    print("Generating audio codes...")
    with torch.inference_mode():
        gen = lm_model.generate(
            input_ids=seq,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            eos_token_id=128258,
            use_cache=True,
        )
    
    # Extract audio codes
    token_to_find = 128257
    positions = (gen == token_to_find).nonzero(as_tuple=True)[1]
    crop = gen[0, positions[-1]+1:] if positions.numel() else gen[0]
    clean = crop[crop != 128258]
    L = (clean.size(0) // 7) * 7
    codes = (clean[:L] - 128266).tolist()
    
    # Decode to waveform
    print("Decoding to audio...")
    audio = redistribute_codes(codes)
    wav = audio.detach().squeeze().cpu().numpy()
    
    # Save to file
    wavfile.write(output_file, 24000, wav)
    print(f"Audio saved to {output_file}")
    
    return wav

# Example usage
if __name__ == "__main__":
    text = "Wo ho te sɛn?"
    voice = "kwaku"  # Options: kwaku, akosua, mawutor, tahiru
    
    synthesize_speech(text, voice=voice, output_file="output.wav")