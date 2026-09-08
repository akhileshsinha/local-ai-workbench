# Local AI Workbench

An end-to-end locally hosted GenAI platform for experimenting with multiple specialized AI models through a unified React interface and Python API layer.

## Overview

Local AI Workbench integrates multiple local models and AI capabilities into a single application:

* **Qwen** — conversational and text generation
* **Qwen-Vision** — image/multimodal understanding
* **Qwen-Coder** — code generation and code modification
* **FLUX** — image generation
* **RAG** — question answering over uploaded documents

The platform uses endpoint-based model routing to invoke the appropriate model based on the requested capability.

## Architecture

React Frontend
↓
Python API Layer
↓
Model Router
├── Qwen
├── Qwen-Vision
├── Qwen-Coder
├── FLUX
└── RAG Pipeline

## Features

### Multi-Model Routing

Routes requests to specialized local models based on the API endpoint and requested capability.

### AI Coding Assistant

A VS Code extension connects to the local Qwen-Coder API and enables prompt-driven code generation and modification.

The extension can create and modify files and folders based on natural-language instructions.

### Document Q&A

Users can upload documents and ask questions about their content using a RAG-based workflow.

### Multimodal AI

Qwen-Vision enables image-aware interactions and visual question answering.

### Image Generation

FLUX is integrated for locally generated images.

### Document Intelligence

The platform supports AI-assisted document generation and modification.

## Key Engineering Concepts

* Local LLM inference
* Multi-model orchestration
* Model routing
* REST APIs
* RAG
* Multimodal AI
* AI coding assistants
* Filesystem/tool integration
* React + Python architecture
* Local AI deployment


                         ┌─────────────────────┐
                         │     React App       │
                         │                     │
                         │ Chat │ Vision │ RAG │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Python API       │
                         │                     │
                         │  Model Router       │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
        ┌─────────┐            ┌──────────┐          ┌──────────┐
        │  Qwen   │            │  Vision  │          │  Coder   │
        │   LLM   │            │  Qwen-V  │          │ Qwen-C   │
        └─────────┘            └──────────┘          └────┬─────┘
                                                           │
                                                           ▼
                                                    ┌─────────────┐
                                                    │ File System │
                                                    └─────────────┘

             ┌──────────────────────┐
             │    RAG Pipeline       │
             │ Documents → Chunks    │
             │ → Embeddings → Search │
             └──────────┬───────────┘
                        │
                        ▼
                   Qwen / LLM

             ┌──────────────────────┐
             │        FLUX          │
             │    Image Generation  │
             └──────────────────────┘

             ┌──────────────────────┐
             │     VS Code          │
             │      Extension       │
             └──────────┬───────────┘
                        │
                        ▼
                   Qwen-Coder
