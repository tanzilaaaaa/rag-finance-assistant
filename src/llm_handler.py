"""
LLM Handler Module
Handles interaction with Language Models for answer generation
"""

from typing import List, Dict, Optional
from config import Config


class LLMHandler:
    """Handle LLM interactions for answer generation"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize LLM handler
        
        Args:
            model_name: Name of the LLM model to use
        """
        self.model_name = model_name or Config.LLM_MODEL
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            print(f"Initialized LLM: {self.model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
    
    def generate_answer(
        self,
        query: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User's question
            context: Retrieved context from vector store
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated answer
        """
        # Construct prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._construct_user_prompt(query, context)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            answer = response.choices[0].message.content
            return answer.strip()
        
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        return """You are an expert financial advisor and investment analyst with deep knowledge of stock markets, investment strategies, and financial planning.

Your role is to provide clear, accurate, and helpful answers to questions about investing, stock markets, and financial strategies based on the provided context from investment textbooks and educational materials.

Guidelines:
1. Base your answers primarily on the provided context
2. Be specific and reference key concepts from the context
3. If the context doesn't fully answer the question, acknowledge this
4. Use clear, professional language appropriate for investors
5. Include relevant examples or analogies when helpful
6. Do not make up information not supported by the context
7. If asked about specific strategies or theories, explain them thoroughly
8. For practical questions, provide actionable insights

Remember: Your goal is to educate and inform based on established investment principles found in the provided materials."""
    
    def _construct_user_prompt(self, query: str, context: str) -> str:
        """
        Construct user prompt with query and context
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        return f"""Based on the following context from investment educational materials, please answer the question below.

Context:
{context}

Question: {query}

Please provide a clear, comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide what information is available."""
    
    def generate_answer_with_sources(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, any]:
        """
        Generate answer and return with source information
        
        Args:
            query: User's question
            retrieved_chunks: List of retrieved chunk dictionaries
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Dictionary with answer and sources
        """
        # Format context from chunks
        context_parts = []
        sources = []
        
        for i, chunk_data in enumerate(retrieved_chunks, 1):
            text = chunk_data.get('text', '')
            metadata = chunk_data.get('metadata', {})
            similarity = chunk_data.get('similarity', 0)
            
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', 'unknown')
            
            context_parts.append(
                f"[Source {i}] (Page {page}, Relevance: {similarity:.3f})\n{text}"
            )
            
            sources.append({
                'source_num': i,
                'source': source,
                'page': page,
                'similarity': similarity,
                'text_preview': text[:200] + "..." if len(text) > 200 else text
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        answer = self.generate_answer(query, context, max_tokens, temperature)
        
        return {
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources),
            'query': query
        }
    
    def generate_streaming_answer(
        self,
        query: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ):
        """
        Generate answer with streaming (for real-time display)
        
        Args:
            query: User's question
            context: Retrieved context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they are generated
        """
        system_prompt = self._get_system_prompt()
        user_prompt = self._construct_user_prompt(query, context)
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def evaluate_answer_quality(
        self,
        query: str,
        answer: str,
        context: str
    ) -> Dict[str, any]:
        """
        Evaluate the quality of a generated answer
        
        Args:
            query: Original question
            answer: Generated answer
            context: Context used
            
        Returns:
            Dictionary with quality metrics
        """
        # Simple quality checks
        quality = {
            'answer_length': len(answer),
            'contains_context_info': any(
                phrase in answer.lower() 
                for phrase in ['based on', 'according to', 'context']
            ),
            'query_terms_addressed': sum(
                1 for term in query.lower().split()
                if len(term) > 3 and term in answer.lower()
            )
        }
        
        # Heuristic quality score
        if quality['answer_length'] > 100 and quality['contains_context_info']:
            quality['quality_score'] = 'good'
        elif quality['answer_length'] > 50:
            quality['quality_score'] = 'acceptable'
        else:
            quality['quality_score'] = 'poor'
        
        return quality
    
    def generate_followup_questions(
        self,
        query: str,
        answer: str,
        num_questions: int = 3
    ) -> List[str]:
        """
        Generate relevant follow-up questions
        
        Args:
            query: Original question
            answer: Generated answer
            num_questions: Number of follow-up questions
            
        Returns:
            List of follow-up questions
        """
        prompt = f"""Based on this Q&A about investing, suggest {num_questions} relevant follow-up questions that would help deepen understanding:

Question: {query}
Answer: {answer}

Generate {num_questions} follow-up questions (one per line):"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            followups = response.choices[0].message.content.strip().split('\n')
            # Clean up questions
            followups = [q.strip('- 0123456789.') for q in followups if q.strip()]
            
            return followups[:num_questions]
        
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return []


# Test function
if __name__ == "__main__":
    print("LLM Handler module - test mode")
    print(f"Model: {Config.LLM_MODEL}")
