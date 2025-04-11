"""
Test script for the DOT Generator.

This script tests the basic functionality of the DOT generator module.
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the DOT generator
from codex_arch.visualization.graph.dot_generator import DotGenerator


def test_with_simple_graph():
    """Test the DOT generator with a simple graph."""
    logger.info("Testing DOT generator with simple graph...")
    
    # Create a simple dependency graph
    dependency_graph = {
        "nodes": {
            "module_a": {"type": "module"},
            "module_b": {"type": "module"},
            "module_c": {"type": "module"}
        },
        "edges": {
            "module_a": ["module_b", "module_c"],
            "module_b": ["module_c"]
        }
    }
    
    # Generate DOT file
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    dot_generator = DotGenerator(output_dir=output_dir)
    digraph = dot_generator.generate_from_dependency_graph(dependency_graph)
    dot_file = dot_generator.save_dot_file("simple_graph")
    
    logger.info(f"DOT file generated at: {dot_file}")
    logger.info("DOT Source:")
    logger.info(dot_generator.to_dot_string())


def test_with_styled_graph():
    """Test the DOT generator with styled nodes and edges."""
    logger.info("Testing DOT generator with styled graph...")
    
    # Create a dependency graph with styling
    dependency_graph = {
        "metadata": {
            "title": "Styled Dependency Graph"
        },
        "nodes": {
            "app/main.py": {
                "type": "file",
                "label": "Main App",
                "important": True
            },
            "app/models/user.py": {
                "type": "class",
                "complexity": 8,
                "show_complexity": True
            },
            "app/controllers/auth.py": {
                "type": "module",
                "size": "45KB",
                "show_size": True
            },
            "app/utils/helpers.py": {
                "type": "function",
                "dependencies": 5,
                "show_deps": True
            },
            "app/views/dashboard.py": {
                "type": "file"
            }
        },
        "edges": {
            "app/main.py": {
                "app/controllers/auth.py": {
                    "type": "imports",
                    "label": "imports",
                    "relationship": "imports"
                },
                "app/views/dashboard.py": {
                    "type": "imports",
                    "relationship": "imports"
                }
            },
            "app/controllers/auth.py": {
                "app/models/user.py": {
                    "type": "uses",
                    "relationship": "uses",
                    "importance": 2.0
                }
            },
            "app/models/user.py": {
                "app/utils/helpers.py": {
                    "type": "uses",
                    "relationship": "uses"
                }
            },
            "app/views/dashboard.py": {
                "app/models/user.py": {
                    "type": "uses",
                    "relationship": "uses",
                    "critical": True
                }
            }
        }
    }
    
    # Generate DOT file with light theme
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Light theme
    dot_generator = DotGenerator(output_dir=output_dir)
    dot_generator.set_theme("light")
    digraph = dot_generator.generate_from_dependency_graph(dependency_graph)
    dot_file = dot_generator.save_dot_file("styled_graph_light")
    
    logger.info(f"Light theme DOT file generated at: {dot_file}")
    
    # Dark theme
    dot_generator = DotGenerator(output_dir=output_dir)
    dot_generator.set_theme("dark")
    digraph = dot_generator.generate_from_dependency_graph(dependency_graph)
    dot_file = dot_generator.save_dot_file("styled_graph_dark")
    
    logger.info(f"Dark theme DOT file generated at: {dot_file}")


def test_with_module_grouping():
    """Test the DOT generator with module grouping and readability optimization."""
    logger.info("Testing DOT generator with module grouping...")
    
    # Create a dependency graph with module structure
    dependency_graph = {
        "metadata": {
            "title": "Module Grouped Dependency Graph",
            "module_depth": 2  # Group by first two parts of path
        },
        "nodes": {
            # App core module
            "app/core/app.py": {"type": "file", "important": True},
            "app/core/config.py": {"type": "file"},
            "app/core/exceptions.py": {"type": "file"},
            
            # Models module
            "app/models/user.py": {"type": "class"},
            "app/models/product.py": {"type": "class"},
            "app/models/order.py": {"type": "class"},
            "app/models/base.py": {"type": "class"},
            
            # Controllers module
            "app/controllers/auth.py": {"type": "module"},
            "app/controllers/products.py": {"type": "module"},
            "app/controllers/orders.py": {"type": "module"},
            
            # Utils module
            "app/utils/helpers.py": {"type": "function"},
            "app/utils/validators.py": {"type": "function"},
            "app/utils/formatters.py": {"type": "function"},
            
            # External dependencies (not grouped)
            "external/db_connector.py": {"type": "package", "no_group": True}
        },
        "edges": {
            # App core dependencies
            "app/core/app.py": {
                "app/core/config.py": {"type": "imports"},
                "app/controllers/auth.py": {"type": "imports"},
                "app/controllers/products.py": {"type": "imports"},
                "app/controllers/orders.py": {"type": "imports"},
                "external/db_connector.py": {"type": "imports", "critical": True}
            },
            "app/core/config.py": {
                "app/utils/helpers.py": {"type": "uses"}
            },
            
            # Controller dependencies
            "app/controllers/auth.py": {
                "app/models/user.py": {"type": "uses", "importance": 2.0},
                "app/core/exceptions.py": {"type": "uses"},
                "app/utils/validators.py": {"type": "uses"}
            },
            "app/controllers/products.py": {
                "app/models/product.py": {"type": "uses", "importance": 1.5},
                "app/utils/formatters.py": {"type": "uses"}
            },
            "app/controllers/orders.py": {
                "app/models/order.py": {"type": "uses", "importance": 1.5},
                "app/models/product.py": {"type": "uses"},
                "app/models/user.py": {"type": "uses"},
                "app/utils/formatters.py": {"type": "uses"}
            },
            
            # Model dependencies
            "app/models/user.py": {
                "app/models/base.py": {"type": "inherits", "relationship": "inherits"},
                "app/utils/validators.py": {"type": "uses"}
            },
            "app/models/product.py": {
                "app/models/base.py": {"type": "inherits", "relationship": "inherits"}
            },
            "app/models/order.py": {
                "app/models/base.py": {"type": "inherits", "relationship": "inherits"},
                "app/utils/helpers.py": {"type": "uses"}
            },
            "app/models/base.py": {
                "external/db_connector.py": {"type": "uses", "critical": True}
            }
        }
    }
    
    # Generate DOT file with module grouping
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Standard layout
    dot_generator = DotGenerator(output_dir=output_dir)
    digraph = dot_generator.generate_from_dependency_graph(dependency_graph)
    dot_file = dot_generator.save_dot_file("module_grouped_graph")
    
    logger.info(f"Module grouped graph generated at: {dot_file}")
    
    # Create a large graph to test layout optimization
    large_graph = {
        "metadata": {
            "title": "Large Dependency Graph",
            "module_depth": 1
        },
        "nodes": {},
        "edges": {}
    }
    
    # Generate 60 nodes and 120 edges for testing layout optimization
    for i in range(1, 61):
        module = f"module{i//10 + 1}" if i > 10 else "module1"
        large_graph["nodes"][f"{module}/node{i}.py"] = {
            "type": "file",
            "important": (i % 10 == 0)  # Mark every 10th node as important
        }
    
    # Add edges (about 120)
    for i in range(1, 61):
        source = f"module{i//10 + 1}/node{i}.py" if i > 10 else "module1/node{i}.py"
        large_graph["edges"][source] = {}
        
        # Add 2 edges from each node
        for j in range(1, 3):
            # Target a node in a different module to test inter-cluster edges
            target_idx = (i + j*10) % 60 + 1
            target = f"module{target_idx//10 + 1}/node{target_idx}.py" if target_idx > 10 else "module1/node{target_idx}.py"
            
            large_graph["edges"][source][target] = {
                "type": "uses",
                "relationship": "uses"
            }
    
    # Generate DOT file with layout optimization for large graph
    dot_generator = DotGenerator(output_dir=output_dir)
    digraph = dot_generator.generate_from_dependency_graph(large_graph)
    dot_file = dot_generator.save_dot_file("optimized_large_graph")
    
    logger.info(f"Optimized large graph generated at: {dot_file}")


def test_svg_rendering_and_output_options():
    """Test SVG rendering and output format options."""
    logger.info("Testing SVG rendering and output options...")
    
    # Create a simple dependency graph for testing
    dependency_graph = {
        "metadata": {
            "title": "Output Options Test Graph"
        },
        "nodes": {
            "module_a": {"type": "module", "label": "Module A"},
            "module_b": {"type": "module", "label": "Module B"},
            "module_c": {"type": "module", "label": "Module C"}
        },
        "edges": {
            "module_a": ["module_b", "module_c"],
            "module_b": ["module_c"]
        }
    }
    
    # Set up the output directory
    output_dir = os.path.join(project_root, "output", "svg_test")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the DOT generator
    dot_generator = DotGenerator(output_dir=output_dir)
    
    # Generate the graph
    digraph = dot_generator.generate_from_dependency_graph(dependency_graph)
    
    try:
        # Test SVG rendering
        svg_data = dot_generator.render_graph(format='svg')
        logger.info(f"SVG data generated (length: {len(svg_data)} bytes)")
        
        # Test saving as SVG file
        svg_file = dot_generator.save_svg_file("output_test_svg")
        logger.info(f"SVG file saved at: {svg_file}")
        
        # Test other output formats (if Graphviz supports them)
        try:
            # Try PNG format
            png_file = dot_generator.save_rendered_file("output_test_png", format='png')
            logger.info(f"PNG file saved at: {png_file}")
            
            # Try PDF format
            pdf_file = dot_generator.save_rendered_file("output_test_pdf", format='pdf')
            logger.info(f"PDF file saved at: {pdf_file}")
        except Exception as e:
            logger.warning(f"Skipping some output formats due to error: {str(e)}")
        
        # Verify files exist
        assert os.path.exists(svg_file), f"SVG file was not created at {svg_file}"
        logger.info("SVG rendering test completed successfully")
    except RuntimeError as e:
        if "Graphviz executables not found" in str(e):
            logger.warning("Skipping SVG rendering tests because Graphviz is not installed")
            logger.warning(str(e))
        else:
            raise
    except Exception as e:
        logger.error(f"Unexpected error in SVG rendering test: {str(e)}")
        raise


if __name__ == "__main__":
    # Run all tests
    test_with_simple_graph()
    test_with_styled_graph()
    test_with_module_grouping()
    test_svg_rendering_and_output_options()
    
    logger.info("All tests completed successfully!") 