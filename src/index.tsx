import {
  ButtonItem,
  definePlugin,
  DialogButton,
  Menu,
  MenuItem,
  Navigation,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  showContextMenu,
  staticClasses,
} from "decky-frontend-lib";
import { VFC, useEffect, useState } from "react";
import { FaShip } from "react-icons/fa";

import logo from "../assets/logo.png";

// interface AddMethodArgs {
//   left: number;
//   right: number;
// }

const Content: VFC<{ serverAPI: ServerAPI }> = ({serverAPI}) => {
  // const [result, setResult] = useState<number | undefined>();

  // const onClick = async () => {
  //   const result = await serverAPI.callPluginMethod<AddMethodArgs, number>(
  //     "add",
  //     {
  //       left: 2,
  //       right: 2,
  //     }
  //   );
  //   if (result.success) {
  //     setResult(result.result);
  //   }
  // };

  return (
    <PanelSection title="Panel Section">
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={(e) =>
            showContextMenu(
              <Menu label="Menu" cancelText="CAAAANCEL" onCancel={() => {
                DeckyPluginLoader.toaster.toast({
                  title: "Summary",
                  body: "Body",
                  //logo: logo
                })
              }}>
                <MenuItem onSelected={() => {}}>Item #1</MenuItem>
                <MenuItem onSelected={() => {}}>Item #2</MenuItem>
                <MenuItem onSelected={() => {}}>Item #3</MenuItem>
              </Menu>,
              e.currentTarget ?? window
            )
          }
        >
          Server says yolo
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <img src={logo} />
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => {
            Navigation.CloseSideMenus();
            Navigation.Navigate("/decky-plugin-test");
          }}
        >
          Router
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

const DeckyPluginRouterTest: VFC = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Navigation.NavigateToLibraryTab()}>
        Go to Library
      </DialogButton>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  serverApi.routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
    exact: true,
  });

  const getEvent = async () => {
    return await serverApi.callPluginMethod<any, any>("get_notification", {});
  }

  let interval = setInterval(async () => {
    let data = await getEvent();
    if(!data.result) return;

    let event = data.result;

    console.log(event)

    let logo = null;
    if(event.icon) {
      logo = <img style={{height: "100%"}} src={event.icon}/>;
    }

    DeckyPluginLoader.toaster.toast({
      title: event.summary,
      body: event.body,
      logo: logo
    })

    /*
    if(event.event === "pair") {
      DeckyPluginLoader.toaster.toast({
        title: "Pairing " + event.deviceName + ", key: " + event.verificationKey,
        duration: 15_000,
        body: <a href="#" onClick={async (e) => {
          e.persist()
          await serverApi.callPluginMethod("trust_device", {device_id: event.deviceId})
          e.target.outerHTML = "Accepted";
          e.target.onClick = null;
        }}>Click to accept</a>
      })
      return;
    }

    if(event.event === "notification") {
      let logo = null;
      if(event.icon) {
        logo = <img style={{height: "100%"}} src={event.icon}/>;
      }
      DeckyPluginLoader.toaster.toast({
        title: event.title,
        body: event.body,
        logo: logo
      })
      return;
    }
    */
  }, 1000)

  return {
    title: <div className={staticClasses.Title}>Decky Notifier</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
      clearInterval(interval);
      serverApi.routerHook.removeRoute("/decky-plugin-test");
    },
  };
});
