    
    def update_keyword_knowledge(
        self,
        record_id: str,
        knowledge: str
    ) -> bool:
        """
        Update the knowledge field for a keyword.
        
        Args:
            record_id: Airtable record ID of the keyword
            knowledge: User-provided expertise/insights
            
        Returns:
            True if successful
        """
        url = f"{self.base_url}/{self.keyword_table_id}/{record_id}"
        
        payload = {
            "fields": {
                "Knowledge": knowledge
            }
        }
        
        try:
            response = requests.patch(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to update knowledge: {e}")
            return False
