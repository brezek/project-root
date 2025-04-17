import React from "react";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

function LibreChatPage() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <MDBox
              display="flex"
              alignItems="center"
              justifyContent="center"
              style={{
                height: "80vh",
                borderRadius: "8px",
                overflow: "hidden",
                backgroundColor: "#f8f9fa",
                boxShadow: "0px 4px 6px rgba(0,0,0,0.1)",
              }}
            >
              <iframe
                src="http://localhost:3091"
                width="100%"
                height="100%"
                style={{
                  border: "none",
                  borderRadius: "8px",
                  width: "100%",
                  height: "100%",
                }}
                title="LibreChat"
              />
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default LibreChatPage;
