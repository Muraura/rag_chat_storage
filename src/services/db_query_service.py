import os
import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.db_util.connection import CommunicationsSQLAlchemyConnectionManager, CommunicationsSQLAlchemyConnectionManagerReadOnly

logger = logging.getLogger(__name__)

class DBQueryService:
    def __init__(self):
        self.connection_manager = CommunicationsSQLAlchemyConnectionManager()
        self.connection_manager_read_only = CommunicationsSQLAlchemyConnectionManagerReadOnly()
        
    async def execute_query(self, query_string, params=None, db=None):
        """
        Execute a raw SQL query and return the results
        
        Parameters:
        -----------
        query_string : str
            The SQL query to execute
        params : dict, optional
            Parameters to pass to the query
        db : Session, optional
            Database session. If not provided, a new session will be created
            
        Returns:
        --------
        list
            List of dictionaries containing the query results
        """
        try:
            # Create a new session if not provided
            if not db:
                session = self.connection_manager.Session()
            else:
                session = db
                
            # Execute the query
            logger.info(f"#db_query_service.py #execute_query #executing_query query:{query_string}")
            
            if params:
                result = session.execute(text(query_string), params)
            else:
                result = session.execute(text(query_string))
                
            # Convert to list of dictionaries
            columns = result.keys()
            results_list = [dict(zip(columns, row)) for row in result.fetchall()]
            
            logger.info(f"#db_query_service.py #execute_query #query_executed_successfully result_count:{len(results_list)}")
            
            # Close session if we created it
            if not db:
                session.close()
                
            return results_list
            
        except Exception as e:
            logger.error(f"#db_query_service.py #execute_query #exception_executing_query #Exception, {e}",
                         exc_info=True)
            # Close session if we created it
            if not db and 'session' in locals():
                session.close()
            raise

    async def execute_query_read_only(self, query_string, params=None, db=None):
        """
        Execute a raw SQL query and return the results
        
        Parameters:
        -----------
        query_string : str
            The SQL query to execute
        params : dict, optional
            Parameters to pass to the query
        db : Session, optional
            Database session. If not provided, a new session will be created
            
        Returns:
        --------
        list
            List of dictionaries containing the query results
        """
        try:
            # Create a new session if not provided
            if not db:
                session = self.connection_manager_read_only.Session()
            else:
                session = db
                
            # Execute the query
            logger.info(f"#db_query_service.py #execute_query_read_only #executing_query query:{query_string}")
            
            if params:
                result = session.execute(text(query_string), params)
            else:
                result = session.execute(text(query_string))
                
            # Convert to list of dictionaries
            columns = result.keys()
            results_list = [dict(zip(columns, row)) for row in result.fetchall()]   
            
            logger.info(f"#db_query_service.py #execute_query_read_only #query_executed_successfully result_count:{len(results_list)}")
            
            # Close session if we created it
            if not db:
                session.close()
                
            return results_list
        
        except Exception as e:
            logger.error(f"#db_query_service.py #execute_query_read_only #exception_executing_query #Exception, {e}",
                         exc_info=True)
            raise
        
    async def query_to_dataframe(self, query_string, params=None, db=None):
        """
        Execute a raw SQL query and return the results as a pandas DataFrame
        
        Parameters:
        -----------
        query_string : str
            The SQL query to execute
        params : dict, optional
            Parameters to pass to the query
        db : Session, optional
            Database session. If not provided, a new session will be created
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing the query results
        """
        try:
            # Get query results
            results = await self.execute_query_read_only(query_string, params)
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            logger.info(f"#db_query_service.py #query_to_dataframe #converted_to_dataframe shape:{df.shape}")
            
            return df
            
        except Exception as e:
            logger.error(f"#db_query_service.py #query_to_dataframe #exception_converting_to_dataframe #Exception, {e}",
                         exc_info=True)
            raise 