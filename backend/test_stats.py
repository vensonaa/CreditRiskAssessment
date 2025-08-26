#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.data_service import DataService

async def test_statistics():
    """Test the statistics methods"""
    data_service = DataService()
    
    try:
        print("Testing statistics methods...")
        
        total_reports = await data_service.get_total_reports()
        total_workflows = await data_service.get_total_workflows()
        completed_workflows = await data_service.get_completed_workflows()
        error_workflows = await data_service.get_error_workflows()
        avg_iterations = await data_service.get_average_iterations()
        avg_duration = await data_service.get_average_duration()
        
        print(f"Total Reports: {total_reports}")
        print(f"Total Workflows: {total_workflows}")
        print(f"Completed Workflows: {completed_workflows}")
        print(f"Error Workflows: {error_workflows}")
        print(f"Average Iterations: {avg_iterations}")
        print(f"Average Duration: {avg_duration}")
        
        # Calculate success rate
        success_rate = 0.0
        if total_workflows > 0:
            success_rate = (completed_workflows / total_workflows) * 100
        
        print(f"Success Rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"Error testing statistics: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_statistics())
