import React, { useState } from "react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

function Tables() {
  const [items, setItems] = useState([
    { id: "1", name: "Project Alpha", status: "In Progress" },
    { id: "2", name: "Project Beta", status: "Completed" },
    { id: "3", name: "Project Gamma", status: "Pending" },
  ]);

  const handleDragEnd = (result) => {
    if (!result.destination) return; // Dropped outside the list

    const newItems = [...items];
    const [reorderedItem] = newItems.splice(result.source.index, 1);
    newItems.splice(result.destination.index, 0, reorderedItem);

    setItems(newItems);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId="table">
                {(provided) => (
                  <div ref={provided.innerRef} {...provided.droppableProps} style={{ padding: 10 }}>
                    {items.map((item, index) => (
                      <Draggable key={item.id} draggableId={item.id} index={index}>
                        {(provided) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            style={{
                              padding: 15,
                              marginBottom: 10,
                              backgroundColor: "#fff",
                              borderRadius: "8px",
                              boxShadow: "0px 4px 6px rgba(0,0,0,0.1)",
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              ...provided.draggableProps.style,
                            }}
                          >
                            <span>{item.name}</span>
                            <span style={{ fontWeight: "bold", color: "#888" }}>{item.status}</span>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Tables;
