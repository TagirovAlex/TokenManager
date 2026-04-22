import requests


def send_to_comfyui(prompt, comfyui_host, api_key=None, timeout=30,
                   negative='', seeds=1, steps=20, cfg=8,
                   width=512, height=512, filename_prefix='prompt_manager',
                   workflow=None):
    if not prompt:
        raise ValueError('prompt is required')
    
    if workflow is None:
        workflow = {
            "3": {
                "inputs": {"text": prompt, "clip": ["4", 0]},
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode"}
            },
            "5": {
                "inputs": {
                    "seeds": seeds,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "positive": ["3", 0],
                    "negative": ["6", 0],
                    "latent_image": ["9", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"}
            },
            "6": {
                "inputs": {"text": negative, "clip": ["4", 0]},
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode"}
            },
            "8": {
                "inputs": {"width": width, "height": height, "batch_size": 1},
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "9": {
                "inputs": {"samples": ["8", 0], "model": ["10", 0]},
                "class_type": "VAEEncode",
                "_meta": {"title": "VAE Encode"}
            },
            "10": {
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Checkpoint Loader"}
            },
            "11": {
                "inputs": {"samples": ["5", 0], "filename_prefix": filename_prefix},
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
    
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    response = requests.post(
        f'{comfyui_host}/prompt',
        json={'prompt': workflow},
        headers=headers,
        timeout=timeout
    )
    
    if response.status_code == 200:
        result = response.json()
        return {
            'message': 'Workflow sent',
            'prompt_id': result.get('prompt_id')
        }
    else:
        raise RuntimeError(f'ComfyUI error: {response.text}')


def get_comfyui_status(prompt_id, comfyui_host):
    response = requests.get(
        f'{comfyui_host}/history/{prompt_id}',
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError('Cannot get status')


def process_webhook(data):
    status = data.get('status', {})
    prompt_id = status.get('prompt_id')
    
    if status.get('completed') and data.get('outputs'):
        return {
            'message': 'Generation completed',
            'prompt_id': prompt_id,
            'outputs': data.get('outputs')
        }
    
    return {
        'message': 'Status received',
        'prompt_id': prompt_id,
        'status': status.get('status')
    }