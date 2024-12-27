// External imports first
import React, { useEffect, useState } from "react";
import { useAtom } from 'jotai';
import { RouteComponentProps, useNavigate } from "@reach/router";

// Then local imports
//import { LoginForm } from 'views/components/metadata-form/loginForm';
import LoginMetadataForm from 'views/components/metadata-form/loginForm';

import Button from "@mui/material/Button";
import { Helmet } from "react-helmet";
import useTranslation from "hooks/use-translation";
import useToast from "hooks/use-toast";
import AppWrapper from "views/components/app-wrapper";
import AppContent from "views/components/app-content";
import SettingsHeader from "views/settings/components/settings-header";
import SettingsContent from "views/settings/components/settings-content";
import SettingsMenu from "views/settings/components/settings-menu";
import MetadataForm from "views/components/metadata-form";
import { keysAtom, profileAtom, ravenAtom } from "atoms";
import { Card, CardContent } from "@mui/material";

import { useModularDAO } from '../../hooks/useModularDAO';
import { familyInfoAtom } from '../../state/web3State';

const SettingsProfilePage = (_: RouteComponentProps) => {
  const [keys] = useAtom(keysAtom);
  const [familyInfo] = useAtom(familyInfoAtom);
  const { getProfileInfo } = useModularDAO();
  const navigate = useNavigate();
  const [t] = useTranslation();
  const [profile] = useAtom(profileAtom);
  const [raven] = useAtom(ravenAtom);
  const [, showMessage] = useToast();
  const [inProgress, setInProgress] = useState<boolean>(false);

  useEffect(() => {
    if (!keys) {
      navigate("/login").then();
    }
  }, [keys]);

  useEffect(() => {
    if (keys?.pub) {
      getProfileInfo();
    }
  }, [keys]);

  return (
    <>
      <Helmet>
        <title>{t("NostrChat - Profile")}</title>
      </Helmet>
      <AppWrapper>
        <SettingsMenu />
        <AppContent>
          <SettingsHeader section={t("Profile")} />

          <div className="col-12 col-md-8 offset-md-2">
            <Card>
              <CardContent>
                <SettingsContent>
                  <LoginMetadataForm
                    values={{
                      name: profile?.name || "",
                      about: profile?.about || "",
                      picture: profile?.picture || "",
                    }}
                    submitBtnLabel={t("Save")}
                    skipButton={<Button />}
                    onSubmit={(data) => {
                      setInProgress(true);
                      raven
                        ?.updateProfile(data)
                        .then(() => {
                          showMessage(t("Your profile updated"), "success");
                          navigate("/settings").then();
                        })
                        .catch((e) => {
                          showMessage(e.toString(), "error");
                        })
                        .finally(() => setInProgress(false));
                    }}
                    inProgress={inProgress}
                  />
                </SettingsContent>
              </CardContent>
            </Card>
          </div>
          {familyInfo && (
            <div>
              <h3>Family Information</h3>
              <p>Family ID: {familyInfo.familyId}</p>
              <p>Family Size: {familyInfo.familySize}</p>
              <p>Relationships: {familyInfo.relationships.length}</p>
            </div>
          )}
        </AppContent>
      </AppWrapper>
    </>
  );
};

export default SettingsProfilePage;
