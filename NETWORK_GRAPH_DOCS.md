# Network Graph Documentation

## Overview
The Network Graph functionality in the IPC/CPC Classification Analysis provides interactive visualization of relationships between companies and patent classifications.

## Features

### 🎯 What the Network Graph Shows
- **Company Nodes** (Blue circles): Top patent holders
- **Classification Nodes** (Red circles): Patent classification codes (IPC/CPC)
- **Edges** (Colored lines): Patent count relationships between companies and classifications
- **Interactive Hover**: Detailed patent information for each node

### 🔧 Technical Implementation

#### Dependencies
- **NetworkX >= 3.0**: Graph creation and layout algorithms
- **Plotly**: Interactive visualization
- **Pandas**: Data processing

#### Key Components

1. **Graph Creation**
   ```python
   G = nx.Graph()
   # Add company and classification nodes
   # Add weighted edges based on patent counts
   ```

2. **Layout Algorithm**
   ```python
   pos = nx.spring_layout(G, k=3, iterations=50)
   ```
   - Uses force-directed layout for optimal node positioning
   - `k=3`: Controls node spacing
   - `iterations=50`: Layout calculation precision

3. **Interactive Features**
   - **Company hover**: Shows all connected classifications and patent counts
   - **Classification hover**: Shows all connected companies and patent counts
   - **Color-coded connections**: Each company has unique edge colors

### 🎨 Visual Design

#### Node Types
- **Companies**: 
  - Size: 25px diameter
  - Color: Light blue with dark blue border
  - Text: Company name (wrapped for long names)

- **Classifications**:
  - Size: 18px diameter  
  - Color: Light coral with dark red border
  - Text: Classification code (formatted for readability)

#### Edge Styling
- **Width**: 2px
- **Color**: Unique color per company (qualitative color palette)
- **Opacity**: 0.7 for better readability
- **Hover**: Shows connection details

### 📊 Data Processing

#### Input Requirements
- DataFrame with columns: `['Current Owner', 'Total', ...classification_codes]`
- Top 8 companies by patent count (for visualization clarity)
- Top 5 classification codes by total activity

#### Edge Weight Calculation
```python
weight = patent_count / 10  # Normalized for visualization
```

## Performance Optimizations

### Current Optimizations
1. **Limited Node Count**: Max 8 companies + 5 classifications = 13 nodes
2. **Efficient Layout**: Spring layout with optimized parameters
3. **Selective Edge Display**: Only non-zero patent count connections
4. **Color-coded Groups**: Organized by company for clarity

### Recommended Enhancements

#### 1. Performance for Large Datasets
```python
# For datasets with many companies/classifications
def optimize_network_for_large_data(df, max_companies=10, max_classifications=6):
    # Filter to top performers only
    # Use hierarchical clustering for node grouping
    # Implement edge bundling for dense connections
```

#### 2. Advanced Visualization Features
```python
# Node sizing based on patent count
node_sizes = [count/10 for count in patent_counts]

# Dynamic edge thickness
edge_widths = [weight*3 for weight in edge_weights]

# Community detection
communities = nx.community.louvain_communities(G)
```

#### 3. Interactive Filtering
```python
# Add Streamlit controls for:
# - Minimum patent count threshold
# - Company/classification selection
# - Time period filtering
# - Technology domain focus
```

## Usage Examples

### Basic Implementation
```python
from app.IPC_CPC_class import create_network_graph

# With processed data
create_network_graph(classification_df, "CPC")
```

### Error Handling
```python
if not NETWORKX_AVAILABLE:
    st.warning("NetworkX not installed. Install with: pip install networkx")
    st.info("Network graph visualization is not available.")
    return
```

## Troubleshooting

### Common Issues

1. **NetworkX Not Available**
   - **Cause**: Missing `networkx` in requirements.txt
   - **Solution**: Add `networkx>=3.0` to requirements.txt
   - **Status**: ✅ RESOLVED

2. **Layout Calculation Slow**
   - **Cause**: Too many nodes or high iteration count
   - **Solution**: Limit nodes to top performers, reduce iterations

3. **Overlapping Nodes**
   - **Cause**: Insufficient spacing parameter
   - **Solution**: Increase `k` parameter in spring_layout

4. **Memory Issues with Large Graphs**
   - **Cause**: Large datasets creating dense networks
   - **Solution**: Pre-filter data, use hierarchical approach

### Performance Metrics
- **Optimal Range**: 5-15 nodes, 10-50 edges
- **Layout Time**: < 1 second for recommended size
- **Render Time**: < 2 seconds for interactive display

## Future Enhancements

### 1. Multi-Level Network Analysis
- **Patent Families**: Group related patents
- **Technology Clusters**: Identify innovation domains
- **Temporal Networks**: Show evolution over time

### 2. Advanced Analytics
- **Centrality Measures**: Identify key players and technologies
- **Community Detection**: Find collaboration patterns
- **Shortest Paths**: Technology transfer routes

### 3. Export Capabilities
- **High-resolution PNG/SVG export**
- **Interactive HTML export**
- **Network data export** (GraphML, GEXF formats)

## Integration Notes

### Streamlit Integration
- Uses `st.plotly_chart()` for display
- Responsive design with `use_container_width=True`
- Error handling with graceful degradation

### Data Pipeline
1. Load classification data
2. Filter to top performers
3. Create NetworkX graph
4. Calculate layout
5. Generate Plotly visualization
6. Display in Streamlit

---

**Last Updated**: 2024-12-18
**Version**: 1.0
**NetworkX Version**: 3.4.2+