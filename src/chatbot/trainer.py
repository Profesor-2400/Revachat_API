"""
Sistema de entrenamiento para el chatbot
"""
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW, get_linear_schedule_with_warmup
from typing import List, Dict, Tuple
import pandas as pd
from tqdm import tqdm
from config import settings


class ChatDataset(Dataset):
    """
    Dataset personalizado para entrenamiento del chatbot
    """
    
    def __init__(self, data: List[Dict], tokenizer, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Combinar pregunta y respuesta
        input_text = f"user: {item['question']}\nassistant: {item['answer']}"
        
        # Tokenizar
        encoding = self.tokenizer(
            input_text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": encoding["input_ids"].flatten()
        }


class ChatbotTrainer:
    """
    Clase para entrenar el modelo de chatbot
    """
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        self.training_stats = {
            "epochs": 0,
            "total_loss": 0,
            "best_loss": float('inf'),
            "history": []
        }
    
    def prepare_data(
        self, 
        training_data: List[Dict],
        validation_split: float = 0.1
    ) -> Tuple[DataLoader, DataLoader]:
        """
        Prepara los datos para entrenamiento
        
        Args:
            training_data: Lista de diccionarios con 'question' y 'answer'
            validation_split: Porcentaje de datos para validación
            
        Returns:
            Tupla de (train_dataloader, val_dataloader)
        """
        # Dividir datos
        val_size = int(len(training_data) * validation_split)
        train_size = len(training_data) - val_size
        
        train_data = training_data[:train_size]
        val_data = training_data[train_size:]
        
        # Crear datasets
        train_dataset = ChatDataset(train_data, self.tokenizer, settings.max_length)
        val_dataset = ChatDataset(val_data, self.tokenizer, settings.max_length)
        
        # Crear dataloaders
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=settings.batch_size,
            shuffle=True
        )
        
        val_dataloader = DataLoader(
            val_dataset,
            batch_size=settings.batch_size,
            shuffle=False
        )
        
        return train_dataloader, val_dataloader
    
    def train(
        self,
        train_dataloader: DataLoader,
        val_dataloader: DataLoader = None,
        epochs: int = None,
        learning_rate: float = None
    ):
        """
        Entrena el modelo
        """
        epochs = epochs or settings.epochs
        learning_rate = learning_rate or settings.learning_rate
        
        # Configurar optimizador
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        
        # Scheduler
        total_steps = len(train_dataloader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        print(f"Iniciando entrenamiento por {epochs} épocas...")
        print(f"Device: {self.device}")
        print(f"Batches por época: {len(train_dataloader)}")
        
        for epoch in range(epochs):
            print(f"\n{'='*50}")
            print(f"Época {epoch + 1}/{epochs}")
            print(f"{'='*50}")
            
            # Entrenamiento
            train_loss = self._train_epoch(train_dataloader, optimizer, scheduler)
            
            # Validación
            val_loss = None
            if val_dataloader:
                val_loss = self._validate(val_dataloader)
            
            # Guardar estadísticas
            self.training_stats["epochs"] += 1
            self.training_stats["history"].append({
                "epoch": epoch + 1,
                "train_loss": train_loss,
                "val_loss": val_loss
            })
            
            # Guardar mejor modelo
            if val_loss and val_loss < self.training_stats["best_loss"]:
                self.training_stats["best_loss"] = val_loss
                print(f"¡Nuevo mejor modelo! Loss: {val_loss:.4f}")
            
            print(f"\nTrain Loss: {train_loss:.4f}")
            if val_loss:
                print(f"Val Loss: {val_loss:.4f}")
        
        print("\n¡Entrenamiento completado!")
        return self.training_stats
    
    def _train_epoch(self, dataloader, optimizer, scheduler):
        """
        Entrena una época
        """
        self.model.train()
        total_loss = 0
        
        progress_bar = tqdm(dataloader, desc="Entrenando")
        
        for batch in progress_bar:
            # Mover batch al device
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)
            
            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            total_loss += loss.item()
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            
            # Clip gradients
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            
            optimizer.step()
            scheduler.step()
            
            # Actualizar barra de progreso
            progress_bar.set_postfix({"loss": loss.item()})
        
        avg_loss = total_loss / len(dataloader)
        return avg_loss
    
    def _validate(self, dataloader):
        """
        Valida el modelo
        """
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Validando"):
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                total_loss += outputs.loss.item()
        
        avg_loss = total_loss / len(dataloader)
        return avg_loss
    
    def get_training_stats(self) -> Dict:
        """
        Obtiene estadísticas del entrenamiento
        """
        return self.training_stats
