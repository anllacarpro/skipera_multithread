# Multithreading Implementation

This document describes the multithreading improvements made to Skipera for faster parallel processing.

## Overview

The multithreading implementation allows Skipera to process multiple course items concurrently, significantly reducing processing time for courses with many items.

## Features

### Parallel Item Processing
- **Videos**: Multiple videos are processed simultaneously
- **Readings**: Readings are marked as complete in parallel
- **Assessments**: Multiple assessments can be solved concurrently (when using LLM)

### Thread Safety
- Each worker thread gets its own HTTP session to avoid conflicts
- Session cookies and headers are properly replicated
- Thread-safe operations with proper locking

### Optimized Video Watching
- Video progress updates are made in parallel where possible
- Reduced waiting times through concurrent API calls

## Usage

### Basic Usage (4 workers - default)
```bash
python main.py --slug your-course-slug --llm
```

### Custom Worker Count
```bash
# Use 8 parallel workers for faster processing
python main.py --slug your-course-slug --llm --workers 8

# Use 2 workers for slower connection or to avoid rate limiting
python main.py --slug your-course-slug --llm --workers 2
```

### Assessment Only Mode (eva)
```bash
# Process only assessments with 6 workers
python main.py --slug your-course-slug --eva --workers 6
```

## Performance Benefits

### Before (Sequential Processing)
- Video 1 → Video 2 → Video 3 → Reading 1 → Assessment 1
- Total time: Sum of all individual processing times

### After (Parallel Processing)
- All items start processing simultaneously (up to worker limit)
- Total time: Approximately the time of the slowest individual task

### Example Performance Improvement
- **Sequential**: 10 videos × 2 minutes each = 20 minutes
- **Parallel (4 workers)**: 10 videos ÷ 4 workers ≈ 5 minutes

## Configuration

### Worker Count Recommendations
- **2-4 workers**: Good for stable connections, avoids rate limiting
- **4-6 workers**: Balanced performance for most users
- **6-8 workers**: Maximum performance for fast connections
- **8+ workers**: May hit rate limits, use with caution

### Network Considerations
- More workers = higher network traffic
- Monitor for HTTP 429 (Too Many Requests) errors
- Reduce worker count if experiencing rate limiting

## Implementation Details

### Main Changes
1. **main.py**: Added `ThreadPoolExecutor` for concurrent item processing
2. **watcher/watch.py**: Optimized video progress updates with parallel API calls
3. **Thread Safety**: Each worker gets isolated HTTP sessions

### New CLI Option
- `--workers N`: Set number of parallel workers (default: 4)

### Thread Architecture
```
Main Thread
├── Worker Thread 1 → Process Video 1
├── Worker Thread 2 → Process Video 2
├── Worker Thread 3 → Process Reading 1
└── Worker Thread 4 → Process Assessment 1
```

## Error Handling
- Individual item failures don't stop other workers
- Failed tasks are logged but processing continues
- Session isolation prevents cascading failures

## Backward Compatibility
- All existing commands work unchanged
- Default behavior (4 workers) provides good performance
- Original sequential logic preserved as fallback